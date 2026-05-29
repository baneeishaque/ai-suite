#!/usr/bin/env python3
"""
renormalize_filtered_files.py — backfill stored blobs through a Git clean filter.

Runs `git add --renormalize` on the set of tracked files matching one or more
pathspecs, with the user-mandated guard that files whose working-tree CONTENT
has changed (true content drift, not just filter-induced phantom changes) are
EXCLUDED from the renormalize batch so the resulting commit is purely a
formatting / filter change.

Dirty detection: compare raw working-tree bytes to the index blob directly via
`git show :PATH`. A file appearing as 'M' in `git status` is NOT proof of
content change — when a clean filter is freshly installed, every matching file
appears modified because clean(working_tree) != blob. That phantom-dirty state
is exactly what this backfill is meant to fix; only TRUE byte-level drift is
worth skipping.

Usage:
    renormalize_filtered_files.py --pattern 'path/to/*.json' [--pattern ...] [--dry-run]

Exit codes:
    0  success (or dry-run completed cleanly)
    1  git command failed
    2  invalid arguments
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_git(args: list[str]) -> str:
    return subprocess.run(
        ["git", *args],
        check=True, text=True, encoding="utf-8", capture_output=True,
    ).stdout


def list_tracked(patterns: list[str]) -> set[str]:
    out: set[str] = set()
    for pat in patterns:
        text = run_git(["ls-files", "-z", "--", pat])
        out.update(p for p in text.split("\x00") if p)
    return out


def is_truly_dirty(path: str) -> bool:
    """Compare raw working-tree bytes to the index blob's raw bytes.

    True iff content has actually changed (not merely filter-induced drift).
    Files missing from the working tree are treated as dirty (skip).
    """
    wt = Path(path)
    if not wt.exists():
        return True
    wt_bytes = wt.read_bytes()
    blob = subprocess.run(
        ["git", "show", f":{path}"],
        check=False, capture_output=True,
    )
    if blob.returncode != 0:
        return True
    return wt_bytes != blob.stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pattern", action="append", required=True,
                    help="Git pathspec; repeat for multiple patterns.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report what would be renormalized without staging.")
    args = ap.parse_args()

    try:
        matching = sorted(list_tracked(args.pattern))
    except subprocess.CalledProcessError as e:
        print(f"ERROR: git failed: {e.stderr}", file=sys.stderr)
        return 1

    to_renormalize: list[str] = []
    skipped_dirty: list[str] = []
    for f in matching:
        if is_truly_dirty(f):
            skipped_dirty.append(f)
        else:
            to_renormalize.append(f)

    print(f"matching tracked files : {len(matching)}")
    print(f"  skipped (true drift) : {len(skipped_dirty)}")
    print(f"  to renormalize       : {len(to_renormalize)}")
    for f in skipped_dirty:
        print(f"  SKIP-DIRTY  {f}")

    if not to_renormalize:
        print("nothing to renormalize.")
        return 0

    if args.dry_run:
        print("[dry-run] would run: git add --renormalize -- <list>")
        return 0

    try:
        subprocess.run(
            ["git", "add", "--renormalize",
             "--pathspec-from-file=-", "--pathspec-file-nul"],
            input="\x00".join(to_renormalize) + "\x00",
            text=True, encoding="utf-8", check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"ERROR: git add --renormalize failed: {e}", file=sys.stderr)
        return 1

    staged = run_git(["diff", "--cached", "--name-only"]).splitlines()
    print(f"staged after renormalize: {len(staged)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
