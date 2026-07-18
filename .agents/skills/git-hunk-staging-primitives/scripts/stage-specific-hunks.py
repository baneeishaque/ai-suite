#!/usr/bin/env python3
"""
stage-specific-hunks.py — Stage specific hunk indices from a file's diff
against HEAD into the Git index, leaving the working tree untouched.

Used when the desired intermediate state corresponds exactly to specific
hunks from the working-tree-vs-HEAD diff (e.g., hunk 0, 2, and 4 of 13).

Mechanism
---------
1. Reads the file's diff from HEAD via `git diff HEAD -- <file>`.
2. Parses the unified diff into header + list of hunks (split on @@ lines).
3. Selects only the hunks at the requested indices (0-based).
4. Reconstructs a filtered patch (header + selected hunks).
5. Stages the filtered patch via `git apply --cached`.

This is a deterministic Tier-A primitive. It does NOT modify the working tree.

Usage
-----
Dry-run (show which hunks would be staged; no staging):
    python3 stage-specific-hunks.py --file SKILL.md --hunks 0 2 4 --dry-run

Stage specific hunk indices:
    python3 stage-specific-hunks.py --file SKILL.md --hunks 0 2 4

Safety
------
- Refuses to run unless inside a Git repository.
- Refuses to stage if zero hunks matched (use --allow-empty-match to override).
- Reports selected hunk ranges to stderr for audit.

See also
--------
- stage-hunk-from-diff.py — stages hunks matching a content pattern.
- stage-file-excluding-lines.py — stages working tree minus matching lines.
- agents-md-stage-row.py — stages exactly one AGENTS.md table row.
- SKILL.md §13 — Intermediate State Synthesis.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd=None, input_bytes=None, check=True):
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        sys.exit(f"FATAL: {' '.join(cmd)} exited {result.returncode}")
    return result


def find_repo_root(start):
    return Path(
        run(["git", "-C", str(start), "rev-parse", "--show-toplevel"]).stdout.decode("utf-8").strip()
    )


def parse_hunks(patch_text: str):
    """Parse a unified-diff patch into (header_lines, [hunk_dicts]).

    Returns:
        header_lines: list of lines before first @@ (includes diff --git, ---, +++)
        hunks: list of dicts with keys 'header' (the @@ line) and 'lines' (content)
    """
    if not patch_text.strip():
        return [], []

    lines = patch_text.splitlines(keepends=True)

    # Find hunk header indices
    hunk_starts = []
    for i, line in enumerate(lines):
        if line.startswith("@@ "):
            hunk_starts.append(i)

    if not hunk_starts:
        return lines, []

    header = lines[: hunk_starts[0]]
    hunks = []
    for idx, start in enumerate(hunk_starts):
        end = hunk_starts[idx + 1] if idx + 1 < len(hunk_starts) else len(lines)
        hunk_lines = lines[start:end]
        hunks.append({"header": hunk_lines[0], "lines": hunk_lines[1:]})

    return header, hunks


def main():
    parser = argparse.ArgumentParser(
        description="Stage specific hunk indices from a file's diff against HEAD.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file", required=True, help="Path to file (relative to repo root).")
    parser.add_argument("--hunks", nargs="+", type=int, required=True,
                        help="0-based hunk indices to stage (e.g., 0 2 4).")
    parser.add_argument("--repo", default=".", help="Path inside target repo (default: cwd).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show matched hunks and run git apply --check; don't stage.")
    parser.add_argument("--allow-empty-match", action="store_true",
                        help="Do not error if zero hunks matched.")
    args = parser.parse_args()

    if not args.hunks:
        sys.exit("FATAL: at least one --hunks index is required.")

    repo = find_repo_root(Path(args.repo).resolve())
    target = Path(args.file)
    if not target.is_absolute():
        target = (Path(args.repo).resolve() / args.file).resolve()
    try:
        rel = target.relative_to(repo).as_posix()
    except ValueError:
        sys.exit(f"FATAL: {target} is not inside repo {repo}")

    if not target.is_file():
        sys.exit(f"FATAL: {target} does not exist or is not a regular file.")

    # Get diff from HEAD
    result = run(["git", "-C", str(repo), "diff", "HEAD", "--no-color", "--", rel], check=False)
    full_diff = result.stdout.decode("utf-8", errors="replace")

    if not full_diff.strip():
        sys.stderr.write(f"file:  {rel}\n")
        sys.stderr.write(f"state: no diff from HEAD\n")
        sys.exit("FATAL: file has no changes from HEAD.")

    header, hunks = parse_hunks(full_diff)

    if not hunks:
        sys.stderr.write(f"file:    {rel}\n")
        sys.stderr.write(f"total:   0 hunks (diff present but no @@ headers?)\n")
        sys.exit("FATAL: no hunks found in diff.")

    # Select hunks
    selected = []
    skipped = []
    for idx in args.hunks:
        if 0 <= idx < len(hunks):
            selected.append(hunks[idx])
        else:
            sys.stderr.write(f"WARNING: hunk index {idx} out of range (0-{len(hunks)-1}), skipping\n")

    if not selected and not args.allow_empty_match:
        sys.stderr.write(f"file:     {rel}\n")
        sys.stderr.write(f"total:    {len(hunks)} hunks\n")
        sys.stderr.write(f"selected: 0 hunks\n")
        sys.exit("FATAL: zero hunks matched. Use --allow-empty-match to override.")

    sys.stderr.write(f"file:     {rel}\n")
    sys.stderr.write(f"source:   HEAD diff (git diff HEAD -- {rel})\n")
    sys.stderr.write(f"total:    {len(hunks)} hunks\n")
    sys.stderr.write(f"selected: {len(selected)} hunks\n")
    for h in selected:
        m = re.match(r"@@\s+(-?\d+(?:,\d+)?)\s+(-?\d+(?:,\d+)?)\s+@@", h["header"])
        if m:
            sys.stderr.write(f"  @@ {m.group(1)} -> {m.group(2)} @@ ({len(h['lines'])} lines)\n")
        else:
            sys.stderr.write(f"  @@ {h['header'].strip()} @@\n")

    if args.dry_run:
        # Build filtered patch and run git apply --check
        filtered_lines = list(header)
        for h in selected:
            filtered_lines.append(h["header"])
            filtered_lines.extend(h["lines"])
        filtered_text = "".join(filtered_lines)

        check_result = run(
            ["git", "-C", str(repo), "apply", "--check", "--cached"],
            input_bytes=filtered_text.encode("utf-8"),
            check=False,
        )
        if check_result.returncode == 0:
            sys.stderr.write(f"CHECK: filtered patch would apply cleanly ({len(selected)} hunk(s) would be staged).\n")
        else:
            sys.stderr.write(check_result.stderr.decode("utf-8", errors="replace"))
            sys.exit("CHECK FAILED: filtered patch would NOT apply cleanly.")
        return

    # Apply matching hunks to index
    filtered_lines = list(header)
    for h in selected:
        filtered_lines.append(h["header"])
        filtered_lines.extend(h["lines"])
    filtered_text = "".join(filtered_lines)

    apply_result = run(
        ["git", "-C", str(repo), "apply", "--cached"],
        input_bytes=filtered_text.encode("utf-8"),
        check=False,
    )
    if apply_result.returncode != 0:
        sys.stderr.write(apply_result.stderr.decode("utf-8", errors="replace"))
        sys.exit("FATAL: git apply --cached failed. Use --dry-run to diagnose.")

    sys.stderr.write(f"OK: {len(selected)} hunk(s) staged. Working tree unchanged.\n")
    sys.stderr.write(f"    Unstaged: {len(hunks) - len(selected)} hunk(s) remain.\n")


if __name__ == "__main__":
    main()