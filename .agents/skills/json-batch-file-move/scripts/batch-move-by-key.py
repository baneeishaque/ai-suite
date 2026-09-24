#!/usr/bin/env python3
"""
batch-move-by-key.py — Base primitive: read a JSON array from stdin, group
entries by a "key" field, create subfolders named after each key, and move
files into their respective subfolders.

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §2.1.
Stdlib only: argparse, json, sys, os, shutil, collections.

CRITICAL: This script NEVER opens/reads/writes source file content.
It uses only os.path.exists, os.makedirs, and shutil.move — all
metadata-only filesystem operations. This is essential for OneDrive-
synced folders where file reads trigger download.

Usage:
  python3 batch-move-by-key.py --target-dir /path/to/parent < input.json
  python3 batch-move-by-key.py --dry-run < input.json
"""

import argparse
import json
import os
import shutil
import sys
from collections import defaultdict


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Move files into key-named subfolders from a JSON manifest"
    )
    p.add_argument(
        "--target-dir",
        default=None,
        help="Parent directory for key subfolders (default: current working directory)",
    )
    p.add_argument("--dry-run", action="store_true", help="Log planned moves; do not execute")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    target_dir = os.path.abspath(args.target_dir) if args.target_dir else os.path.abspath(os.getcwd())

    if not os.path.isdir(target_dir):
        print(f"error: target directory does not exist: {target_dir}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON on stdin — {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print("error: stdin must contain a JSON array", file=sys.stderr)
        sys.exit(1)

    if not data:
        print("error: input array is empty", file=sys.stderr)
        sys.exit(1)

    # Validate and group by key
    groups: dict[str, list[dict]] = defaultdict(list)
    errors: list[dict] = []
    for item in data:
        if not isinstance(item, dict):
            errors.append({"abspath": "", "key": "", "status": "error", "error": "non-dict element"})
            continue
        abspath = item.get("abspath")
        key = item.get("key")
        if not abspath or not key:
            errors.append({
                "abspath": str(abspath or ""),
                "key": str(key or ""),
                "status": "error",
                "error": "missing required field 'abspath' or 'key'",
            })
            continue
        if not os.path.exists(abspath):
            errors.append({
                "abspath": abspath,
                "key": str(key),
                "status": "error",
                "error": "file does not exist",
            })
            continue
        groups[str(key)].append(item)

    if not groups and errors:
        # All entries had errors — report and exit
        json.dump(errors, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        sys.exit(1)

    # Process each group
    results: list[dict] = list(errors)  # carry forward pre-validation errors

    for key, items in sorted(groups.items()):
        key_dir = os.path.join(target_dir, key)
        if not args.dry_run:
            os.makedirs(key_dir, exist_ok=True)

        for item in items:
            abspath = item["abspath"]
            basename = os.path.basename(abspath)
            dest = os.path.join(key_dir, basename)

            if args.dry_run:
                print(f"[dry-run] mv {abspath} -> {dest}", file=sys.stderr)
                results.append({
                    "abspath": abspath,
                    "key": key,
                    "status": "dry-run",
                    "error": None,
                })
                continue

            try:
                shutil.move(abspath, dest)
                results.append({
                    "abspath": abspath,
                    "key": key,
                    "status": "moved",
                    "error": None,
                })
            except OSError as e:
                results.append({
                    "abspath": abspath,
                    "key": key,
                    "status": "error",
                    "error": str(e),
                })

    json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
