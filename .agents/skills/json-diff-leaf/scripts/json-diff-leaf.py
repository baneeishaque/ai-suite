#!/usr/bin/env python3
"""
json-diff-leaf — Recursive leaf-value diff of two JSON files.

Outputs a JSON array of change objects to stdout. Each change object:
  {"path": "a.b.c", "kind": "added|removed|changed|type-changed|reordered",
   "old_value": …, "new_value": …}

Exit 0 (no differences or only differences found), exit 1 on error.

This is the BASE primitive — no human-readable formatting, no timestamp
detection, no conclusions. See the json-diff-cli composer for that.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Any


def diff_structures(a: Any, b: Any) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []

    def _diff(a: Any, b: Any, path: str) -> None:
        if type(a) is not type(b):
            changes.append({
                "path": path,
                "kind": "type-changed",
                "old_value": type(a).__name__,
                "new_value": type(b).__name__,
            })
            return

        if isinstance(a, dict):
            all_keys = set(a) | set(b)
            for k in sorted(all_keys):
                child = f"{path}.{k}" if path else k
                if k not in a:
                    changes.append({
                        "path": child,
                        "kind": "added",
                        "new_value": b[k],
                    })
                elif k not in b:
                    changes.append({
                        "path": child,
                        "kind": "removed",
                        "old_value": a[k],
                    })
                else:
                    _diff(a[k], b[k], child)

        elif isinstance(a, list):
            old_serialized = set(map(json.dumps, a))
            new_serialized = set(map(json.dumps, b))
            added = [json.loads(s) for s in new_serialized - old_serialized]
            removed_vals = [json.loads(s) for s in old_serialized - new_serialized]

            if added:
                changes.append({
                    "path": path,
                    "kind": "added",
                    "new_value": added,
                })
            if removed_vals:
                changes.append({
                    "path": path,
                    "kind": "removed",
                    "old_value": removed_vals,
                })
            if not added and not removed_vals and a != b:
                changes.append({
                    "path": path,
                    "kind": "reordered",
                    "old_value": a,
                    "new_value": b,
                })

        else:
            if a != b:
                changes.append({
                    "path": path,
                    "kind": "changed",
                    "old_value": a,
                    "new_value": b,
                })

    _diff(a, b, "")
    return changes


def main() -> None:
    parser = argparse.ArgumentParser(description="Recursive JSON leaf-value diff")
    parser.add_argument("--file1", required=True, type=Path, help="First JSON file")
    parser.add_argument("--file2", required=True, type=Path, help="Second JSON file")
    args = parser.parse_args()

    a: Any = json.loads(args.file1.read_bytes())
    b: Any = json.loads(args.file2.read_bytes())

    changes = diff_structures(a, b)
    json.dump(changes, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
