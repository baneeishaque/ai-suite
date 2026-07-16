#!/usr/bin/env python3
"""
split-flat-folder.py — Composer: orchestrate a 3-base pipeline to split a
flat OneDrive folder into key-named subfolders, respecting the 5000-file
OneDrive web preview limit.

Pipeline:
  1. file-glob-sort-by-regex-capture/scripts/sort-by-capture.py
     → JSON Lines (abspath, key, filename, size, mtime)
  2. Convert JSONL → JSON array
  3. json-group-stats/scripts/group-stats.py --group-by key --output counts
     → per-group file counts
  4. Check: any group >= threshold? Warn / prompt.
  5. If not dry-run: json-batch-file-move/scripts/batch-move-by-key.py
     → execute moves
  6. Print summary

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §2.1.
Stdlib only: argparse, json, sys, subprocess, os.

Usage:
  python3 split-flat-folder.py --directory /path/to/folder --glob "*.png" --regex "(2025-\d{2})"
  python3 split-flat-folder.py --directory /path/to/folder --glob "Screenshot*.png" --regex "(20\d{2}-\d{2})" --dry-run
"""

import argparse
import json
import os
import subprocess
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Base script paths (anchored to this script's location)
BASE_SORT = os.path.join(
    SCRIPT_DIR,
    "../../file-glob-sort-by-regex-capture/scripts/sort-by-capture.py",
)
BASE_GROUP = os.path.join(
    SCRIPT_DIR,
    "../../json-group-stats/scripts/group-stats.py",
)
BASE_MOVE = os.path.join(
    SCRIPT_DIR,
    "../../json-batch-file-move/scripts/batch-move-by-key.py",
)


def verify_bases() -> None:
    missing = [p for p in [BASE_SORT, BASE_GROUP, BASE_MOVE] if not os.path.exists(p)]
    if missing:
        print("error: required base scripts not found:", file=sys.stderr)
        for p in missing:
            print(f"  {p}", file=sys.stderr)
        sys.exit(1)


def run_sort_by_capture(directory: str, glob_pattern: str, regex: str) -> list[dict]:
    """Run the glob+regex base script and return parsed JSON array."""
    result = subprocess.run(
        [sys.executable, BASE_SORT, "--directory", directory, "--glob", glob_pattern, "--regex", regex],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"error: sort-by-capture failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Parse JSON Lines → JSON array
    records: list[dict] = []
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"warning: skipping malformed JSONL line: {e}", file=sys.stderr)
            continue

    if not records:
        print("error: no files matched the glob + regex pattern", file=sys.stderr)
        sys.exit(1)

    return records


def run_group_stats(records: list[dict]) -> list[dict]:
    """Run the group-stats base and return per-group counts."""
    input_json = json.dumps(records)
    result = subprocess.run(
        [sys.executable, BASE_GROUP, "--group-by", "key", "--output", "counts"],
        input=input_json,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"error: group-stats failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    try:
        counts = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"error: failed to parse group-stats output: {e}", file=sys.stderr)
        sys.exit(1)

    return counts


def run_batch_move(records: list[dict], target_dir: str, dry_run: bool) -> None:
    """Run the batch-move base to execute file moves."""
    input_json = json.dumps(records)
    cmd = [sys.executable, BASE_MOVE, "--target-dir", target_dir]
    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(
        cmd,
        input=input_json,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"error: batch-move failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Print move results
    print(result.stdout)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Split a flat OneDrive folder into key-named subfolders"
    )
    p.add_argument("--directory", required=True, help="Flat folder to organize")
    p.add_argument("--glob", required=True, help="Glob pattern for target files")
    p.add_argument("--regex", required=True, help="Regex with capture group for grouping key")
    p.add_argument("--threshold", type=int, default=5000, help="Max files per output folder (default: 5000)")
    p.add_argument("--dry-run", action="store_true", help="Report only; do not move files")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f"error: directory does not exist: {directory}", file=sys.stderr)
        sys.exit(1)

    verify_bases()

    # Step 1: Glob + regex capture → JSON array
    print(f"[1/4] Scanning: {args.glob} in {directory}", file=sys.stderr)
    records = run_sort_by_capture(directory, args.glob, args.regex)
    print(f"       Found {len(records)} file(s)", file=sys.stderr)

    # Step 2: Group stats → per-group counts
    print(f"[2/4] Grouping by key...", file=sys.stderr)
    counts = run_group_stats(records)
    print(f"       {len(counts)} group(s) found", file=sys.stderr)

    # Step 3: Check threshold
    print(f"[3/4] Checking threshold ({args.threshold})...", file=sys.stderr)
    over_threshold = [c for c in counts if c["count"] >= args.threshold]
    under_threshold = [c for c in counts if c["count"] < args.threshold]

    print(file=sys.stderr)
    print("  Groups:", file=sys.stderr)
    for c in counts:
        flag = " *** OVER THRESHOLD ***" if c["count"] >= args.threshold else ""
        print(f"    {c['key']}: {c['count']} file(s){flag}", file=sys.stderr)
    print(file=sys.stderr)

    if over_threshold:
        print(
            f"  WARNING: {len(over_threshold)} group(s) meet or exceed the {args.threshold}-file threshold.",
            file=sys.stderr,
        )
        print(
            "  OneDrive web preview may not display all files in these folders.",
            file=sys.stderr,
        )
        if not args.dry_run:
            response = input("  Continue with move? [y/N] ").strip().lower()
            if response != "y":
                print("  Aborted by user.", file=sys.stderr)
                sys.exit(0)
    elif not args.dry_run:
        # Automatically confirm if under threshold
        print(f"  All groups are under the {args.threshold}-file threshold. Proceeding.", file=sys.stderr)

    # Step 4: Execute moves
    if args.dry_run:
        print("[4/4] Dry-run — no files moved.", file=sys.stderr)
        run_batch_move(records, directory, dry_run=True)
    else:
        print(f"[4/4] Moving files...", file=sys.stderr)
        run_batch_move(records, directory, dry_run=False)

    # Summary
    total_over = sum(c["count"] for c in over_threshold)
    total_under = sum(c["count"] for c in under_threshold)
    print(file=sys.stderr)
    print(f"  Summary: {total_over} file(s) in over-threshold groups, {total_under} in under-threshold groups.", file=sys.stderr)
    print(f"  Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
