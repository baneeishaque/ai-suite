#!/usr/bin/env python3
"""
audit_filtered_blobs.py — verify stored blobs are in their post-filter form.

For each tracked file matching one or more pathspecs, fetches the stored blob
via `git show :PATH` and counts newlines. Classifies pretty/minified by a
line-count threshold (default 3 — minified JSON typically has 0–2 lines).

Usage:
    audit_filtered_blobs.py --pattern 'path/to/*.json' [--pattern ...] [--min-lines N]

Exit codes:
    0  all matching blobs are pretty
    1  one or more blobs are still minified
    2  invalid arguments / git error
"""
from __future__ import annotations

import argparse
import subprocess
import sys


def run_git(args: list[str]) -> str:
    return subprocess.run(
        ["git", *args],
        check=True, text=True, encoding="utf-8", capture_output=True,
    ).stdout


def list_tracked(pattern: str) -> list[str]:
    text = run_git(["ls-files", "-z", "--", pattern])
    return [p for p in text.split("\x00") if p]


def blob_line_count(path: str) -> int:
    try:
        blob = subprocess.run(
            ["git", "show", f":{path}"],
            check=True, text=True, encoding="utf-8", capture_output=True,
        ).stdout
    except subprocess.CalledProcessError:
        return -1
    return blob.count("\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pattern", action="append", required=True,
                    help="Git pathspec; repeat for multiple patterns.")
    ap.add_argument("--min-lines", type=int, default=3,
                    help="Lines threshold below which a blob is 'minified' (default 3).")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    total_minified = 0
    print(f"{'pretty':>7}  {'minified':>9}  pattern")
    print("-" * 60)
    for pat in args.pattern:
        try:
            files = list_tracked(pat)
        except subprocess.CalledProcessError as e:
            print(f"ERROR: {e.stderr}", file=sys.stderr)
            return 2
        pretty = 0
        minified = 0
        for f in files:
            n = blob_line_count(f)
            if n < args.min_lines:
                minified += 1
                if args.verbose:
                    print(f"  MIN  ({n} lines)  {f}")
            else:
                pretty += 1
        total_minified += minified
        print(f"{pretty:>7}  {minified:>9}  {pat}")
    print("-" * 60)
    print(f"total minified across all patterns: {total_minified}")
    return 0 if total_minified == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
