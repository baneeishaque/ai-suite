#!/usr/bin/env python3
"""
find-entry.py — Locate chat.tools.terminal.autoApprove entries.

Part of the vscode-terminal-autoapprove-audit skill.
See ../SKILL.md §4.3 for usage context.

Usage:
    # Print entry at a 0-based index (or 1-based with --one-based)
    python3 find-entry.py --settings <path> --index 5

    # Search by substring against the (raw) regex key
    python3 find-entry.py --settings <path> --grep "ssh-mcp"

    # List all entries with their indices (key truncated to 80 chars)
    python3 find-entry.py --settings <path> --list

Exit codes:
    0  found / printed
    1  not found / out of range
    2  argument error
"""

import argparse
import json
import sys


def load_entries(path: str):
    with open(path, encoding="utf-8") as fp:
        data = json.load(fp)
    return list(data.get("chat.tools.terminal.autoApprove", {}).items())


def truncate(text: str, n: int = 80) -> str:
    flat = text.replace("\n", "\\n")
    return flat if len(flat) <= n else flat[:n] + "..."


def main() -> int:
    parser = argparse.ArgumentParser(description="Find/list autoApprove entries.")
    parser.add_argument("--settings", required=True, help="Path to settings.json")
    parser.add_argument("--one-based", action="store_true",
                        help="Treat --index as 1-based (default: 0-based)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--index", type=int, help="Print entry at this index")
    group.add_argument("--grep", help="Print entries whose key contains substring")
    group.add_argument("--list", action="store_true", help="List all entries")
    args = parser.parse_args()

    entries = load_entries(args.settings)
    total = len(entries)

    if args.list:
        print(f"Total entries: {total}")
        for i, (k, _) in enumerate(entries):
            print(f"  [{i:>2}] {truncate(k)}")
        return 0

    if args.index is not None:
        idx = args.index - 1 if args.one_based else args.index
        if not (0 <= idx < total):
            print(f"ERROR: index {args.index} out of range (0..{total - 1})",
                  file=sys.stderr)
            return 1
        k, v = entries[idx]
        print(f"Index    : {idx} (1-based: {idx + 1})")
        print(f"Key      : {k}")
        print(f"Value    : {v}")
        return 0

    # --grep
    needle = args.grep
    hits = [(i, k, v) for i, (k, v) in enumerate(entries) if needle in k]
    if not hits:
        print(f"No entries matching: {needle!r}", file=sys.stderr)
        return 1
    print(f"{len(hits)} match(es) for {needle!r}:")
    for i, k, v in hits:
        print(f"  [{i:>2}] {truncate(k, 120)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
