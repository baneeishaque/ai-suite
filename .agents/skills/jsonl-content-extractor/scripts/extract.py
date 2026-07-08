#!/usr/bin/env python3
"""
Extract typed content blocks from JSONL files using key-path navigation.

See ../SKILL.md for the full CLI contract.
"""

import argparse
import json
import sys
from typing import Any


def _navigate(node: Any, keys: list[tuple[str, list[str] | None]], depth: int, line_no: int,
              line_data: dict, results: list[dict]):
    if depth >= len(keys):
        return

    key, values = keys[depth]

    if isinstance(node, dict):
        if key not in node:
            return
        val = node[key]
        if values is not None:
            if isinstance(val, str) and val not in values:
                return
            if isinstance(val, list) and not any(v in values for v in val):
                return
            # match confirmed
            if depth == len(keys) - 1:
                is_matched = True
                if isinstance(val, list):
                    for i, item in enumerate(val):
                        results.append({
                            "line": line_no,
                            "line_data": line_data,
                            "content_index": i,
                            "matched": True,
                            "value": item if isinstance(item, str) else json.dumps(item),
                            "block": item,
                        })
                else:
                    results.append({
                        "line": line_no,
                        "line_data": line_data,
                        "content_index": 0,
                        "matched": is_matched,
                        "value": val if isinstance(val, str) else json.dumps(val),
                        "block": node,
                    })
                return
            # non-terminal with values: filter at current level, then continue from same node
            _navigate(node, keys, depth + 1, line_no, line_data, results)
            return
        if depth == len(keys) - 1:
            is_matched = values is None or (isinstance(val, str) and val in values)
            if isinstance(val, list) and values is not None:
                for i, item in enumerate(val):
                    results.append({
                        "line": line_no,
                        "line_data": line_data,
                        "content_index": i,
                        "matched": True,
                        "value": item if isinstance(item, str) else json.dumps(item),
                        "block": item,
                    })
            else:
                results.append({
                    "line": line_no,
                    "line_data": line_data,
                    "content_index": 0,
                    "matched": is_matched,
                    "value": val,
                    "block": node,
                })
        else:
            _navigate(val, keys, depth + 1, line_no, line_data, results)

    elif isinstance(node, list):
        for i, item in enumerate(node):
            if isinstance(item, dict):
                if key in item:
                    item_val = item[key]
                    if values is not None and item_val not in values:
                        continue
                    if depth == len(keys) - 1:
                        is_matched = values is None or item_val in values
                        results.append({
                            "line": line_no,
                            "line_data": line_data,
                            "content_index": i,
                            "matched": is_matched,
                            "value": item_val,
                            "block": item,
                        })
                    else:
                        _navigate(item, keys, depth + 1, line_no, line_data, results)
                elif depth < len(keys) - 1:
                    _navigate(item, keys, depth, line_no, line_data, results)
            elif isinstance(item, str) and depth == len(keys) - 1:
                is_matched = values is None or item in values
                results.append({
                    "line": line_no,
                    "line_data": line_data,
                    "content_index": i,
                    "matched": is_matched,
                    "value": item,
                    "block": item,
                })

    elif depth == len(keys) - 1:
        is_matched = values is None or node in values
        results.append({
            "line": line_no,
            "line_data": line_data,
            "content_index": 0,
            "matched": is_matched,
            "value": node,
            "block": node,
        })


def extract_blocks(
    filepath: str,
    keys: list[tuple[str, list[str] | None]],
) -> tuple[list[dict], list[dict]]:
    results: list[dict] = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            _navigate(data, keys, 0, line_no, data, results)

    matched = [r for r in results if r["matched"]]
    unmatched = [r for r in results if not r["matched"]]
    return matched, unmatched


def _parse_key_arg(arg: str) -> tuple[str, list[str] | None]:
    if ":" in arg:
        key, values_str = arg.split(":", 1)
        values = [v.strip() for v in values_str.split(",") if v.strip()]
        return key, values if values else None
    return arg, None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract typed content blocks from JSONL files via key-path navigation"
    )
    parser.add_argument("--file", required=True, help="Path to input JSONL file")
    parser.add_argument("--key", action="append", default=[],
                        help="Key path segment, optionally with comma-separated values: "
                             "'name' or 'name:val1,val2'")
    parser.add_argument("--output-matched", required=True, help="Path for matched items JSON")
    parser.add_argument("--output-unmatched", required=True, help="Path for unmatched items JSON")

    args = parser.parse_args()

    if not args.key:
        print("Error: at least one --key is required", file=sys.stderr)
        return 1

    keys = [_parse_key_arg(k) for k in args.key]

    # terminal key may omit values to match everything at that level

    matched, unmatched = extract_blocks(args.file, keys)

    with open(args.output_matched, "w", encoding="utf-8") as f:
        json.dump(matched, f, indent=2, ensure_ascii=False)

    with open(args.output_unmatched, "w", encoding="utf-8") as f:
        json.dump(unmatched, f, indent=2, ensure_ascii=False)

    print(f"Matched: {len(matched)}, Unmatched: {len(unmatched)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
