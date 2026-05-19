#!/usr/bin/env python3
"""
audit-autoapprove.py — Batch drop tool for chat.tools.terminal.autoApprove entries.

Part of the vscode-terminal-autoapprove-audit skill.
See ../SKILL.md §9 for usage context.

Usage:
    python3 audit-autoapprove.py --settings <path/to/settings.json> --drop-indices 0 1 2 3

Options:
    --settings       Path to the VS Code settings.json file (required).
    --drop-indices   Space-separated list of 0-based indices to remove (required).
    --dry-run        Print what would be removed without modifying the file.
"""

import argparse
import json
import re
import sys


def load_raw(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_raw(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def validate_json(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON invalid after edit: {e}", file=sys.stderr)
        sys.exit(1)


def fix_trailing_comma(content: str) -> str:
    """Remove trailing commas before } or ] to fix JSON after block removal."""
    return re.sub(r",(\s*[\}\]])", r"\1", content)


def remove_entries(raw: str, keys_to_drop: list[str]) -> str:
    for key in keys_to_drop:
        enc = json.dumps(key)
        # Match the full block: 4-space indent + key: { ... },?\n
        pattern = re.compile(
            r'    ' + re.escape(enc) + r': \{\n'
            r'        "approve": true,\n'
            r'        "matchCommandLine": true\n'
            r'    \},?\n'
        )
        new_raw, n = pattern.subn("", raw, count=1)
        if n != 1:
            print(f"WARN: could not remove key (preview): {key[:80]!r}", file=sys.stderr)
        raw = new_raw
    return raw


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch drop autoApprove entries.")
    parser.add_argument("--settings", required=True, help="Path to settings.json")
    parser.add_argument("--drop-indices", nargs="+", type=int, required=True,
                        metavar="N", help="0-based indices to drop")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview only, do not write")
    args = parser.parse_args()

    raw = load_raw(args.settings)
    data = validate_json(raw)

    aa = data.get("chat.tools.terminal.autoApprove", {})
    keys = list(aa.keys())
    total_before = len(keys)

    invalid = [i for i in args.drop_indices if i < 0 or i >= total_before]
    if invalid:
        print(f"ERROR: indices out of range (max {total_before - 1}): {invalid}",
              file=sys.stderr)
        sys.exit(1)

    keys_to_drop = [keys[i] for i in sorted(set(args.drop_indices))]

    print(f"Entries before: {total_before}")
    for idx, k in zip(sorted(set(args.drop_indices)), keys_to_drop):
        print(f"  DROP [{idx}]: {k[:80].replace(chr(10), chr(92)+'n')}")

    if args.dry_run:
        print("Dry-run — no changes written.")
        return

    new_raw = remove_entries(raw, keys_to_drop)
    new_raw = fix_trailing_comma(new_raw)
    result = validate_json(new_raw)

    total_after = len(result.get("chat.tools.terminal.autoApprove", {}))
    write_raw(args.settings, new_raw)
    print(f"Removed {total_before - total_after} entries. autoApprove entries now: {total_after}")


if __name__ == "__main__":
    main()
