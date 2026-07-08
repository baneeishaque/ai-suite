#!/usr/bin/env python3
"""Recursive directory tree auditor.

Walks a directory tree, counts direct children per folder, flags those
exceeding a configurable threshold. Outputs JSON for consumption by other
skills (e.g., human-scanable-organization).
"""

import argparse
import json
import os
import sys


def audit_folder(root: str, threshold: int) -> list[dict]:
    """Walk `root`, return a sorted list of folder audits."""
    results = []
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        item_count = len(dirnames) + len(filenames)
        rel_path = os.path.relpath(dirpath, root)
        if rel_path == ".":
            rel_path = "/"
        else:
            rel_path = "/" + rel_path
        results.append({
            "path": rel_path,
            "item_count": item_count,
            "dir_count": len(dirnames),
            "file_count": len(filenames),
            "flagged": item_count > threshold,
        })
    results.sort(key=lambda r: r["path"])
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit a directory tree: count items per folder, flag overstuffing."
    )
    parser.add_argument(
        "--root", required=True,
        help="Root directory to audit (required)."
    )
    parser.add_argument(
        "--threshold", type=int, default=10,
        help="Item count threshold for flagging (default: 10)."
    )
    parser.add_argument(
        "--json", action="store_true", default=True,
        help="Output as JSON (always-on; flag present for explicitness)."
    )
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        print(json.dumps({"error": f"root not found or not a directory: {args.root}"}))
        sys.exit(1)

    results = audit_folder(args.root, args.threshold)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
