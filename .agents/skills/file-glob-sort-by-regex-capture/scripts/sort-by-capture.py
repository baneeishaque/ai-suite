#!/usr/bin/env python3
"""
sort-by-capture.py — Base primitive: sort files matched by glob according to a
regex capture group extracted from each filename, optionally filtered to a
numeric span via --min / --max.

Outputs JSON Lines to stdout: one object per file with fields
  filename, key, key_type, size_bytes, mtime_epoch

Usage:
  python3 sort-by-capture.py \\
      --directory /path/to/dir \\
      --glob "video-*.webm" \\
      --regex "video-(\\d+)" \\
      [--sort-type int] \\
      [--reverse] \\
      [--min 30] [--max 36]
"""

import argparse
import glob as glob_module
import json
import os
import re
import sys


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sort files by regex capture from filename")
    p.add_argument("--directory", required=True, help="Directory to scan")
    p.add_argument("--glob", required=True, help="Glob pattern (e.g. video-*.webm)")
    p.add_argument("--regex", required=True, help="Regex with at least one capture group")
    p.add_argument(
        "--sort-type",
        default="int",
        choices=["int", "float", "str"],
        help="Data type of the captured key for sorting (default: int)",
    )
    p.add_argument("--reverse", action="store_true", help="Sort descending")
    p.add_argument(
        "--min",
        type=int,
        default=None,
        help="Drop entries whose numeric captured key is below this value (inclusive); "
        "requires --sort-type int or float",
    )
    p.add_argument(
        "--max",
        type=int,
        default=None,
        help="Drop entries whose numeric captured key is above this value (inclusive); "
        "requires --sort-type int or float",
    )
    return p.parse_args()


def numeric_key(entry: dict, sort_type: str) -> int | float:
    converter = int if sort_type == "int" else float
    return converter(entry["key"])


def main() -> None:
    args = parse_args()

    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f"error: directory does not exist: {directory}", file=sys.stderr)
        sys.exit(1)

    pattern = os.path.join(directory, args.glob)
    files = sorted(glob_module.glob(pattern))
    if not files:
        print("error: no files matched the glob pattern", file=sys.stderr)
        sys.exit(1)

    regex = re.compile(args.regex)

    entries: list[dict] = []
    for fp in files:
        basename = os.path.basename(fp)
        m = regex.search(basename)
        if not m or not m.lastindex:
            print(
                f"warning: regex did not match capture group in: {basename}",
                file=sys.stderr,
            )
            continue
        raw_key = m.group(1)
        stat_info = os.stat(fp)
        entries.append(
            {
                "filename": basename,
                "abspath": fp,
                "key": raw_key,
                "key_type": args.sort_type,
                "size_bytes": stat_info.st_size,
                "mtime_epoch": int(stat_info.st_mtime),
            }
        )

    if not entries:
        print("error: no files matched the regex capture group", file=sys.stderr)
        sys.exit(1)

    # Numeric span filter (--min / --max). Only valid for numeric sort types.
    if args.min is not None or args.max is not None:
        if args.sort_type not in ("int", "float"):
            print(
                "error: --min/--max require --sort-type int or float "
                f"(got '{args.sort_type}')",
                file=sys.stderr,
            )
            sys.exit(2)
        entries = [
            e
            for e in entries
            if (args.min is None or numeric_key(e, args.sort_type) >= args.min)
            and (args.max is None or numeric_key(e, args.sort_type) <= args.max)
        ]
        if not entries:
            print("error: no files matched the numeric range", file=sys.stderr)
            sys.exit(1)

    # Sort by key according to specified type
    if args.sort_type == "int":
        entries.sort(key=lambda e: int(e["key"]), reverse=args.reverse)
    elif args.sort_type == "float":
        entries.sort(key=lambda e: float(e["key"]), reverse=args.reverse)
    else:
        entries.sort(key=lambda e: e["key"], reverse=args.reverse)

    out_lines = [json.dumps(e, ensure_ascii=False) for e in entries]
    sys.stdout.write("\n".join(out_lines) + "\n")


if __name__ == "__main__":
    main()
