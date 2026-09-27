"""
merge-bookmarks.py — Merge two .vscode/bookmarks.json files.

Reads source and target bookmark files, merges entries by path,
deduplicates bookmarks by (line, column), sorts bookmarks by line
then column, sorts file entries by path, and outputs the merged result.

Usage:
    python3 merge-bookmarks.py --source <source.json> --target <target.json> [--output <out.json>] [--dry-run]

Language tier: Tier 1 (Python 3.12+) per scripting-language-selection-rules.
SSOT: vscode-bookmarks-merge skill.
"""

import argparse
import json
import sys
from pathlib import Path


def load_bookmarks(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root value must be a JSON object")
    if "files" not in data:
        data["files"] = []
    if not isinstance(data["files"], list):
        raise ValueError(f"{path}: 'files' must be a JSON array")
    return data


def normalize_path(p: str) -> str:
    """Lowercase for case-insensitive path matching."""
    return p.lower()


def deduplicate_bookmarks(bookmarks: list) -> list:
    seen = set()
    result = []
    for bm in bookmarks:
        line = bm.get("line")
        col = bm.get("column")
        if line is not None and col is not None:
            key = (line, col)
            if key in seen:
                continue
            seen.add(key)
        result.append(bm)
    return result


def sort_bookmarks(bookmarks: list) -> list:
    def sort_key(bm):
        return (bm.get("line", 0), bm.get("column", 0))
    return sorted(bookmarks, key=sort_key)


def merge(source: dict, target: dict) -> dict:
    # Build lookup from target entries keyed by normalized path
    target_by_path = {}
    for entry in target.get("files", []):
        path = entry.get("path", "")
        target_by_path[normalize_path(path)] = entry

    # Merge source entries into target
    merged_files = list(target.get("files", []))

    for src_entry in source.get("files", []):
        src_path = src_entry.get("path", "")
        norm = normalize_path(src_path)
        if norm in target_by_path:
            # Merge bookmarks into existing entry
            existing = target_by_path[norm]
            existing_bms = existing.get("bookmarks", [])
            src_bms = src_entry.get("bookmarks", [])
            combined = existing_bms + src_bms
            combined = deduplicate_bookmarks(combined)
            combined = sort_bookmarks(combined)
            existing["bookmarks"] = combined
        else:
            # New entry — add it
            merged_files.append(
                {
                    "path": src_path,
                    "bookmarks": sort_bookmarks(
                        deduplicate_bookmarks(src_entry.get("bookmarks", []))
                    ),
                }
            )

    # Deduplicate and sort ALL entries (in case target already had dups)
    final_by_path = {}
    for entry in merged_files:
        path = entry.get("path", "")
        norm = normalize_path(path)
        if norm in final_by_path:
            existing = final_by_path[norm]
            combined = existing.get("bookmarks", []) + entry.get("bookmarks", [])
            combined = deduplicate_bookmarks(combined)
            combined = sort_bookmarks(combined)
            existing["bookmarks"] = combined
        else:
            entry["bookmarks"] = sort_bookmarks(
                deduplicate_bookmarks(entry.get("bookmarks", []))
            )
            final_by_path[norm] = entry

    result_files = sorted(final_by_path.values(), key=lambda e: e.get("path", "").lower())
    return {"files": result_files}


def main():
    parser = argparse.ArgumentParser(
        description="Merge two .vscode/bookmarks.json files"
    )
    parser.add_argument(
        "--source", required=True, type=Path, help="Source bookmarks JSON file"
    )
    parser.add_argument(
        "--target", required=True, type=Path, help="Target bookmarks JSON file"
    )
    parser.add_argument(
        "--output", type=Path, default=None, help="Output path (default: stdout)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print merged result to stdout only",
    )
    args = parser.parse_args()

    if not args.source.exists():
        print(f"Error: source file not found: {args.source}", file=sys.stderr)
        sys.exit(2)
    if not args.target.exists():
        print(f"Error: target file not found: {args.target}", file=sys.stderr)
        sys.exit(2)

    try:
        source_data = load_bookmarks(args.source)
        target_data = load_bookmarks(args.target)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    result = merge(source_data, target_data)
    output = json.dumps(result, indent="\t") + "\n"

    if args.dry_run or args.output is None:
        sys.stdout.write(output)
    else:
        args.output.write_text(output, encoding="utf-8")

    if args.dry_run:
        print("--- dry-run complete (no files written) ---", file=sys.stderr)


if __name__ == "__main__":
    main()
