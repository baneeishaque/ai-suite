#!/usr/bin/env python3
"""
stage-head-synthesize.py — Stage a HEAD-synthesized version of a file into the
Git index, applying literal and/or regex replacements on the HEAD blob, leaving
the working tree untouched.

Used during §13 Intermediate State Synthesis of the Atomic Commit Construction
workflow: when the working tree contains interleaved changes that cannot be
cleanly split via hunk-based staging, and the desired intermediate state can
be derived by transforming the committed HEAD version rather than the working
tree.

Mechanism
---------
1. Reads HEAD:<file> via `git show HEAD:<file>`.
2. Applies --replace transformations (literal substring replacement).
3. Applies --regex-replace transformations (re.search / re.sub).
4. Writes the result as a new blob via `git hash-object -w --stdin`.
5. Stages the blob via `git update-index --cacheinfo`.
6. Working tree is never modified.

Match semantics
---------------
- --replace OLD|NEW: replace every occurrence of OLD with NEW.
  OLD is treated as a literal substring, not a regex.
- --regex-replace PATTERN|REPL: treat PATTERN as a regex via re.search /
  re.sub. The replacement follows Python re.sub rules (\\1, \\g<name>, etc.).
- Multiple --replace and --regex-replace flags are applied in order.
- If zero replacements are made and --allow-empty-match is not set, the
  script exits with an error (safety guard).

Usage
-----
Dry-run (show what would be staged; no staging):
    python3 stage-head-synthesize.py \\
        --file SKILL.md \\
        --replace "old text|new text" \\
        --dry-run

Stage with two literal replacements:
    python3 stage-head-synthesize.py \\
        --file AGENTS.md \\
        --replace "Foo Bar|Baz Qux" \\
        --replace "old-path|new-path"

Stage with regex replacement:
    python3 stage-head-synthesize.py \\
        --file dev-env/SKILL.md \\
        --regex-replace "configurations-private|<private-repo>"

Safety
------
- Refuses to run unless inside a Git repository.
- Refuses to stage if zero replacements were made (use --allow-empty-match
  to override when a no-op stage is intentional).
- Reports replacement counts per pattern to stderr for audit.

See also
--------
- agents-md-stage-row.py — sibling script for HEAD + one-new-row staging.
- stage-file-excluding-lines.py — sibling script for working-tree-minus-lines
  staging.
- stage-hunk-from-diff.py — sibling script for selective hunk staging.
- SKILL.md §13 — Intermediate State Synthesis.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd=None, input_bytes=None):
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
        sys.exit(f"FATAL: {' '.join(cmd)} exited {result.returncode}")
    return result.stdout


def find_repo_root(start: str) -> Path:
    return Path(
        run(["git", "-C", start, "rev-parse", "--show-toplevel"]).strip()
    )


def get_index_mode(repo: Path, rel: str) -> str:
    out = run(["git", "-C", str(repo), "ls-files", "--stage", "--", rel])
    if not out.strip():
        return "100644"
    return out.split()[0]


def read_head(repo: Path, rel: str) -> str:
    """Return the HEAD content of *rel*, decoded as UTF-8."""
    try:
        raw = run(["git", "-C", str(repo), "show", f"HEAD:{rel}"])
    except SystemExit:
        sys.exit(f"FATAL: HEAD:{rel} does not exist or is not a file.")
    return raw.decode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synthesize a staged file from HEAD with --replace and "
                    "--regex-replace, leaving the working tree untouched.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file", required=True, help="Path to file (relative to repo root).")
    parser.add_argument("--replace", action="append", default=[], metavar="OLD|NEW",
                        help="Literal replacement: replace OLD with NEW. Repeatable.")
    parser.add_argument("--regex-replace", action="append", default=[], metavar="PATTERN|REPL",
                        help="Regex replacement: replace PATTERN with REPL (re.sub). Repeatable.")
    parser.add_argument("--repo", default=".",
                        help="Path inside the target repo (default: cwd).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show replacements; do not stage.")
    parser.add_argument("--allow-empty-match", action="store_true",
                        help="Do not error if zero replacements were made.")

    args = parser.parse_args()

    if not args.replace and not args.regex_replace:
        sys.exit("FATAL: at least one --replace or --regex-replace is required.")

    repo = find_repo_root(args.repo)
    rel = args.file.replace("\\", "/")

    head_text = read_head(repo, rel)
    text = head_text
    total_replacements = 0

    # -- literal replacements
    for spec in args.replace:
        if "|" not in spec:
            sys.exit(f"FATAL: --replace '{spec}' has no '|' separator (expected OLD|NEW).")
        old, new = spec.split("|", 1)
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            total_replacements += count
            sys.stderr.write(f"[replace]  {count} occurrence(s): {old!r} -> {new!r}\n")
        else:
            sys.stderr.write(f"[replace]  0 occurrences: {old!r}\n")

    # -- regex replacements
    for spec in args.regex_replace:
        if "|" not in spec:
            sys.exit(
                f"FATAL: --regex-replace '{spec}' has no '|' separator "
                f"(expected PATTERN|REPL)."
            )
        pattern_str, repl_str = spec.split("|", 1)
        try:
            pat = re.compile(pattern_str)
        except re.error as exc:
            sys.exit(f"FATAL: invalid regex {pattern_str!r}: {exc}")
        count = len(pat.findall(text))
        if count:
            text = pat.sub(repl_str, text)
            total_replacements += count
            sys.stderr.write(
                f"[regex-replace]  {count} occurrence(s): {pattern_str!r} -> {repl_str!r}\n"
            )
        else:
            sys.stderr.write(
                f"[regex-replace]  0 occurrences: {pattern_str!r}\n"
            )

    sys.stderr.write(f"\ntotal replacements: {total_replacements}\n")

    if not total_replacements and not args.allow_empty_match:
        sys.exit("FATAL: zero replacements made. Use --allow-empty-match to override.")

    if args.dry_run:
        sys.stderr.write("DRY-RUN: no staging performed.\n")
        return

    # Write new blob and stage it
    new_bytes = text.encode("utf-8")
    sha = run(
        ["git", "-C", str(repo), "hash-object", "-w", "--stdin"],
        input_bytes=new_bytes,
    ).strip()
    mode = get_index_mode(repo, rel)
    run(
        ["git", "-C", str(repo), "update-index", "--add", "--cacheinfo",
         f"{mode},{sha},{rel}"],
    )

    sys.stderr.write(f"staged blob: {sha}\n")
    sys.stderr.write(f"OK: {rel} staged from HEAD with {total_replacements} replacement(s) "
                     f"(working tree unchanged).\n")


if __name__ == "__main__":
    main()
