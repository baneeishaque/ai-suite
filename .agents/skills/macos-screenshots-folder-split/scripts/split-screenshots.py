#!/usr/bin/env python3
"""
split-screenshots.py — Domain composer: convenience wrapper around
onedrive-flat-folder-split-by-size with macOS screenshot and screen
recording filename defaults.

Runs TWO passes (one for screenshots, one for recordings) and prints a
combined summary.

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §2.1.
Stdlib only: argparse, subprocess, sys, os.

Usage:
  python3 split-screenshots.py --directory /path/to/Screenshots
  python3 split-screenshots.py --directory /path/to/Screenshots --dry-run --threshold 3000
"""

import argparse
import os
import subprocess
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Composer script path (anchored to this script's location)
COMPOSER = os.path.join(
    SCRIPT_DIR,
    "../../onedrive-flat-folder-split-by-size/scripts/split-flat-folder.py",
)


def verify_composer() -> None:
    if not os.path.exists(COMPOSER):
        print(f"error: required composer script not found: {COMPOSER}", file=sys.stderr)
        sys.exit(1)


def run_pass(directory: str, glob_pattern: str, regex: str, threshold: int, dry_run: bool) -> subprocess.CompletedProcess:
    """Run a single pipeline pass for one glob pattern."""
    cmd = [
        sys.executable,
        COMPOSER,
        "--directory", directory,
        "--glob", glob_pattern,
        "--regex", regex,
        "--threshold", str(threshold),
    ]
    if dry_run:
        cmd.append("--dry-run")

    print(f"=== Pass: glob={glob_pattern} ===", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    # Print stderr from pipeline (progress, warnings, summary)
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    # Print stdout (JSON results) to stdout
    if result.stdout:
        print(result.stdout, end="")

    return result


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Organize a macOS Screenshots folder by date (YYYY-MM subfolders)"
    )
    p.add_argument("--directory", required=True, help="Screenshots folder to organize")
    p.add_argument("--threshold", type=int, default=5000, help="Max files per output folder (default: 5000)")
    p.add_argument("--dry-run", action="store_true", help="Report only; do not move files")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f"error: directory does not exist: {directory}", file=sys.stderr)
        sys.exit(1)

    verify_composer()

    # Regex captures YYYY-MM from both Screenshot and Screen Recording filenames
    # Examples:
    #   "Screenshot 2025-11-14 at 20.42.45.png"         → key=2025-11
    #   "Screenshot 2025-11-14 at 20.42.45 1.png"        → key=2025-11  (the " 1" suffix variant)
    #   "Screen Recording 2025-12-05 at 22.05.29.mov"    → key=2025-12
    regex = r"(20\d{2}-\d{2})"

    # Pass 1: Screenshots (PNG)
    result1 = run_pass(directory, "Screenshot*.png", regex, args.threshold, args.dry_run)

    # Pass 2: Screen Recordings (MOV)
    result2 = run_pass(directory, "Screen Recording*.mov", regex, args.threshold, args.dry_run)

    # Combined summary
    total_files = 0
    total_moved = 0
    total_errors = 0

    for result in [result1, result2]:
        if result.stdout:
            try:
                import json
                items = json.loads(result.stdout)
                total_files += len(items)
                for item in items:
                    if item.get("status") == "moved":
                        total_moved += 1
                    elif item.get("status") == "error":
                        total_errors += 1
            except (json.JSONDecodeError, Exception):
                pass

    print(file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    if args.dry_run:
        print(f"DRY-RUN SUMMARY", file=sys.stderr)
    else:
        print(f"COMPLETED SUMMARY", file=sys.stderr)
    print(f"  Screenshots pass: exit code {result1.returncode}", file=sys.stderr)
    print(f"  Recordings pass:  exit code {result2.returncode}", file=sys.stderr)
    if total_files > 0:
        print(f"  Total files processed: {total_files}", file=sys.stderr)
        print(f"  Moved: {total_moved}", file=sys.stderr)
        print(f"  Errors: {total_errors}", file=sys.stderr)
    print("=" * 50, file=sys.stderr)

    overall_rc = 0
    if result1.returncode != 0:
        overall_rc = result1.returncode
    if result2.returncode != 0 and overall_rc == 0:
        overall_rc = result2.returncode

    sys.exit(overall_rc)


if __name__ == "__main__":
    main()
