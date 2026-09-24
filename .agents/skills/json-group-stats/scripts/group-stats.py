#!/usr/bin/env python3
"""
group-stats.py — Base primitive: read a JSON array from stdin, group elements
by a specified field, and emit per-group counts or grouped records.

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §2.1.
Stdlib only: argparse, json, sys, collections.

Usage:
  python3 group-stats.py --group-by severity --output counts < input.json
  python3 group-stats.py --group-by date --output groups --min-items 5 < input.json
"""

import argparse
import json
import sys
from collections import defaultdict


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Group JSON objects by a field and emit stats")
    p.add_argument("--group-by", required=True, help="Field name to group by")
    p.add_argument(
        "--output",
        default="counts",
        choices=["counts", "groups"],
        help="Output mode: 'counts' (default) or 'groups'",
    )
    p.add_argument("--min-items", type=int, default=None, help="Only include groups with >= N items")
    return p.parse_args()


def main() -> None:
    args = parse_args()

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

    groups: dict[str, list[dict]] = defaultdict(list)
    missing = 0
    for item in data:
        if not isinstance(item, dict):
            print(f"warning: skipping non-dict element: {item}", file=sys.stderr)
            continue
        key = item.get(args.group_by)
        if key is None:
            missing += 1
            continue
        groups[str(key)].append(item)

    if missing:
        print(f"warning: {missing} element(s) missing field '{args.group_by}'", file=sys.stderr)

    if not groups:
        print("error: no elements matched the group-by field", file=sys.stderr)
        sys.exit(1)

    # Build output
    result: list[dict] = []
    for key, items in sorted(groups.items()):
        count = len(items)
        if args.min_items is not None and count < args.min_items:
            continue
        if args.output == "counts":
            result.append({"key": key, "count": count})
        else:
            result.append({"key": key, "count": count, "items": items})

    if not result:
        print(f"note: no groups met --min-items={args.min_items}", file=sys.stderr)
        sys.exit(0)

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
