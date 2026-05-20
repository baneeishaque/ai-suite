#!/usr/bin/env python3
"""
stage-file-excluding-lines.py — Stage a file into the Git index with one or
more lines removed, leaving the working tree untouched.

Used during §2f.1 (Deferred Cross-Reference Hunk Pattern) of the Atomic
Commit Construction workflow: when commit B introduces artifact X and the
working tree of file F (e.g., an AGENTS.md table, a SKILL.md "Related
Skills" table, or a docs index) ALREADY contains a row referencing
artifact Y that will not be created until later commit C, the row must
be absent from commit B's snapshot of F but present in commit C's.

This script writes a "working tree minus matching lines" blob, stages it
via `git update-index --cacheinfo`, and never touches the working tree.
The deferred row(s) remain on disk and are picked up cleanly by a later
`git add <file>` for commit C.

Mechanism
---------
1. Reads the CURRENT WORKING-TREE version of `<file>`.
2. Removes every line whose content matches any --exclude pattern.
3. Writes the result as a new blob via `git hash-object -w`.
4. Updates the index entry for `<file>` via `git update-index --cacheinfo`.
5. Working tree is never modified.

Result: `<file>` is staged with the deferred lines removed. All other
working-tree changes to `<file>` are staged as-is. The deferred lines
remain in the working tree and can be staged in a subsequent commit
via a plain `git add <file>`.

Match semantics
---------------
- `--exclude SUBSTRING`: line is excluded if SUBSTRING appears anywhere
  on it. Repeatable.
- `--exclude-regex PATTERN`: line is excluded if `re.search(PATTERN, line)`
  matches. Repeatable.
- A line matches if ANY supplied pattern matches it.

Usage
-----
Dry-run (show which lines would be excluded; no staging):
    python3 stage-file-excluding-lines.py \
        --file AGENTS.md \
        --exclude "command-autoapprove-onboarding" \
        --dry-run

Stage the file with two patterns excluded:
    python3 stage-file-excluding-lines.py \
        --file .agents/skills/foo/SKILL.md \
        --exclude "../bar/SKILL.md" \
        --exclude-regex '\| \[`baz`\]'

Safety
------
- Refuses to run unless inside a Git repository.
- Refuses to stage if zero lines matched (use --allow-empty-match to
  override).
- Reports excluded line content to stderr for audit.

See also
--------
- agents-md-stage-row.py — sibling script for HEAD + one-new-row staging.
- SKILL.md §2f.1 — Deferred Cross-Reference Hunk Pattern.
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
    return result.stdout.decode("utf-8", errors="replace")


def find_repo_root(start):
    return Path(run(["git", "-C", str(start), "rev-parse", "--show-toplevel"]).strip())


def get_index_mode(repo, rel):
    out = run(["git", "-C", str(repo), "ls-files", "--stage", "--", rel])
    if not out.strip():
        return "100644"
    return out.split()[0]


def main():
    parser = argparse.ArgumentParser(
        description="Stage a file into the index with matching lines removed.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file", required=True, help="Path to file (rel or abs).")
    parser.add_argument("--exclude", action="append", default=[], metavar="SUBSTRING",
                        help="Substring match — exclude any line containing it. Repeatable.")
    parser.add_argument("--exclude-regex", action="append", default=[], metavar="PATTERN",
                        help="Regex match — exclude any line where re.search matches. Repeatable.")
    parser.add_argument("--repo", default=".", help="Path inside the target repo (default: cwd).")
    parser.add_argument("--dry-run", action="store_true", help="Show matched lines; do not stage.")
    parser.add_argument("--allow-empty-match", action="store_true",
                        help="Do not error if zero lines matched.")
    args = parser.parse_args()

    if not args.exclude and not args.exclude_regex:
        sys.exit("FATAL: at least one --exclude or --exclude-regex is required.")

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

    raw = target.read_bytes()
    text = raw.decode("utf-8")
    keeps_newline = text.endswith("\n")
    lines = text.splitlines()

    regexes = [re.compile(p) for p in args.exclude_regex]
    substrings = list(args.exclude)

    kept = []
    removed = []
    for idx, line in enumerate(lines, start=1):
        hit = any(s in line for s in substrings) or any(rx.search(line) for rx in regexes)
        if hit:
            removed.append((idx, line))
        else:
            kept.append(line)

    sys.stderr.write(f"file:       {rel}\n")
    sys.stderr.write(f"original:   {len(lines)} lines\n")
    sys.stderr.write(f"excluded:   {len(removed)} lines\n")
    for ln, content in removed:
        sys.stderr.write(f"  L{ln}: {content}\n")
    sys.stderr.write(f"staged:     {len(kept)} lines\n")

    if not removed and not args.allow_empty_match:
        sys.exit("FATAL: zero lines matched. Use --allow-empty-match to override.")

    if args.dry_run:
        sys.stderr.write("DRY-RUN: no staging performed.\n")
        return

    new_text = "\n".join(kept) + ("\n" if keeps_newline else "")
    new_bytes = new_text.encode("utf-8")

    sha = run(["git", "-C", str(repo), "hash-object", "-w", "--stdin"],
              input_bytes=new_bytes).strip()
    mode = get_index_mode(repo, rel)
    run(["git", "-C", str(repo), "update-index", "--add", "--cacheinfo",
         f"{mode},{sha},{rel}"])

    sys.stderr.write(f"staged blob: {sha}\n")
    sys.stderr.write(f"OK: {rel} staged with {len(removed)} line(s) deferred (working tree unchanged).\n")


if __name__ == "__main__":
    main()
