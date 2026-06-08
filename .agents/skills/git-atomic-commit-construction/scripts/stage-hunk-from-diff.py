#!/usr/bin/env python3
"""
stage-hunk-from-diff.py — Stage only specific hunks of a file's diff into the
Git index, leaving the working tree and non-matching hunks untouched.

Used during hunk-based staging (Step 3 of Atomic Commit Construction) when
`git add -p` hunk boundaries don't align with logical boundaries, or when
performing the staging programmatically inside a scripted workflow.

The workflow:
    git diff -- <file>          # full patch against HEAD
    parse hunks                 # split on @@ markers
    filter by --match           # keep only hunks containing the substring/regex
    git apply --cached          # stage only the filtered hunks

This is the inverse of `stage-file-excluding-lines.py`: that script stages a
file MINUS matching lines; this script stages ONLY matching hunks.

Usage
-----
Dry-run (show which hunks would be staged; no staging):
    python3 stage-hunk-from-diff.py \\
        --file SKILL.md \\
        --match "Phase 1g" \\
        --check

Stage hunks containing a specific substring:
    python3 stage-hunk-from-diff.py \\
        --file SKILL.md \\
        --match "stash-apply"

Stage hunks matching a regex:
    python3 stage-hunk-from-diff.py \\
        --file SKILL.md \\
        --match-regex "Phase\s+1[g-h]"

Stage hunks matching ANY of multiple patterns:
    python3 stage-hunk-from-diff.py \\
        --file SKILL.md \\
        --match "stash-apply" \\
        --match "live editor"

Stage hunks from the staged diff (--cached) instead of unstaged:
    python3 stage-hunk-from-diff.py \\
        --file SKILL.md \\
        --match "Phase 1g" \\
        --cached

Safety
------
- Refuses to run unless inside a Git repository.
- Exits with error if the file has no diff or zero hunks matched.
- Reports matched hunk ranges to stderr for audit.
- Supports --check (dry-run + git apply --check) to verify the filtered patch
  would apply cleanly without modifying index.

See also
--------
- stage-file-excluding-lines.py — stage a file MINUS matching lines.
- agents-md-stage-row.py — stage a single AGENTS.md row.
- SKILL.md §3h — Selective Hunk Extraction via Diff Patching.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
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
    """Parse a unified-diff patch into a list of (header_lines, hunk_chunk) tuples.

    The header includes everything before the first @@ hunk header.
    Each hunk starts with a @@ line and includes everything until the next @@
    or end of file.
    """
    if not patch_text.strip():
        return [], []

    lines = patch_text.splitlines(keepends=True)

    # Find hunk header indices: lines starting with @@
    hunk_starts = []
    for i, line in enumerate(lines):
        if line.startswith("@@ "):
            hunk_starts.append(i)

    if not hunk_starts:
        # No hunks — return the entire patch as "header" (e.g., only diff --git line)
        return lines, []

    header = lines[: hunk_starts[0]]
    hunks = []
    for idx, start in enumerate(hunk_starts):
        end = hunk_starts[idx + 1] if idx + 1 < len(hunk_starts) else len(lines)
        hunks.append(lines[start:end])

    return header, hunks


def hunk_lines_text(hunk_lines):
    """Return the concatenated text of a hunk for pattern matching.

    Strips the leading +/-/space prefix before matching so the pattern
    can match any line type (context, old, new).
    """
    text = "".join(hunk_lines)
    return text


def hunk_matches(hunk_lines, substrings, regexes):
    """Return True if any line in the hunk matches any of the patterns."""
    raw = "".join(hunk_lines)
    for s in substrings:
        if s in raw:
            return True
    for rx in regexes:
        if rx.search(raw):
            return True
    return False


def format_hunk_range(hunk_lines):
    """Extract @@ -a,b +c,d @@ for display."""
    for line in hunk_lines:
        if line.startswith("@@"):
            m = re.match(r"@@\s+(-?\d+(?:,\d+)?)\s+(-?\d+(?:,\d+)?)\s+@@", line)
            if m:
                return f"{m.group(1)} -> {m.group(2)}"
    return "unknown"


def main():
    parser = argparse.ArgumentParser(
        description="Stage matching hunks from a file's diff into the Git index.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file", required=True, help="Path to file (relative or absolute).")
    parser.add_argument("--match", action="append", default=[], metavar="SUBSTRING",
                        help="Substring match — stage hunks containing this. Repeatable.")
    parser.add_argument("--match-regex", action="append", default=[], metavar="PATTERN",
                        help="Regex match — stage hunks matching re.search. Repeatable.")
    parser.add_argument("--cached", action="store_true",
                        help="Diff the index (staged changes) instead of the working tree.")
    parser.add_argument("--check", action="store_true",
                        help="Dry-run: show matched hunks and run git apply --check; don't stage.")
    parser.add_argument("--repo", default=".", help="Path inside the target repo (default: cwd).")
    args = parser.parse_args()

    if not args.match and not args.match_regex:
        sys.exit("FATAL: at least one --match or --match-regex is required.")

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

    regexes = [re.compile(p) for p in args.match_regex]
    substrings = list(args.match)

    # Build git diff command
    diff_cmd = ["git", "-C", str(repo), "diff", "--no-color", "--"]
    if args.cached:
        diff_cmd.insert(3, "--cached")
    diff_cmd.append(rel)

    result = run(diff_cmd, check=False)
    patch = result.stdout.decode("utf-8", errors="replace")

    if not patch.strip():
        sys.stderr.write(f"file:  {rel}\n")
        sys.stderr.write(f"state: {'staged' if args.cached else 'unstaged'} → NO CHANGES\n")
        sys.exit("FATAL: file has no diff to extract hunks from.")

    header, hunks = parse_hunks(patch)

    if not hunks:
        sys.stderr.write(f"file:    {rel}\n")
        sys.stderr.write(f"total:   0 hunks (diff present but no @@ headers?)\n")
        sys.exit("FATAL: no hunks found in diff.")

    # Filter hunks
    matched = []
    unmatched = []
    for hunk in hunks:
        if hunk_matches(hunk, substrings, regexes):
            matched.append(hunk)
        else:
            unmatched.append(hunk)

    sys.stderr.write(f"file:     {rel}\n")
    sys.stderr.write(f"source:   {'staged (--cached)' if args.cached else 'unstaged (working tree)'}\n")
    sys.stderr.write(f"total:    {len(hunks)} hunks\n")
    sys.stderr.write(f"matched:  {len(matched)} hunks\n")
    for h in matched:
        sys.stderr.write(f"  @@ {format_hunk_range(h)} @@  ({len(h)} lines)\n")
    sys.stderr.write(f"skipped:  {len(unmatched)} hunks\n")

    if not matched:
        sys.exit("FATAL: zero hunks matched the supplied pattern(s).")

    if args.check:
        # Build filtered patch and run git apply --check
        filtered_patch_lines = list(header)
        for h in matched:
            filtered_patch_lines.extend(h)
        filtered_text = "".join(filtered_patch_lines)

        check_result = run(
            ["git", "-C", str(repo), "apply", "--check", "--cached"],
            input_bytes=filtered_text.encode("utf-8"),
            check=False,
        )
        if check_result.returncode == 0:
            sys.stderr.write(f"CHECK: filtered patch would apply cleanly "
                             f"({len(matched)} hunk(s) would be staged).\n")
        else:
            sys.stderr.write(check_result.stderr.decode("utf-8", errors="replace"))
            sys.exit("CHECK FAILED: filtered patch would NOT apply cleanly.")
        return

    # Apply matching hunks to the index
    filtered_patch_lines = list(header)
    for h in matched:
        filtered_patch_lines.extend(h)
    filtered_text = "".join(filtered_patch_lines)

    apply_result = run(
        ["git", "-C", str(repo), "apply", "--cached"],
        input_bytes=filtered_text.encode("utf-8"),
        check=False,
    )
    if apply_result.returncode != 0:
        sys.stderr.write(apply_result.stderr.decode("utf-8", errors="replace"))
        sys.exit("FATAL: git apply --cached failed. Use --check to diagnose.")
    sys.stderr.write(f"OK: {len(matched)} hunk(s) staged. Working tree unchanged.\n")
    sys.stderr.write(f"    Unstaged: {len(unmatched)} hunk(s) remain.\n")


if __name__ == "__main__":
    main()
