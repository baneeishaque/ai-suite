#!/usr/bin/env python3
"""
fix-indents.py — Restore all canonical indent overrides for a VS Code settings.json.

Part of the vscode-terminal-autoapprove-audit skill.
See ../SKILL.md §3.1 for the formatting contract.

Run this after ANY edit that rewrites the file (edit-entry.py, audit-autoapprove.py,
or a manual json.dump call).

Overrides applied:
  1. chat.tools.terminal.autoApprove — approve / matchCommandLine: 6sp -> 8sp
  2. files.associations                — values:                    4sp -> 6sp

Usage:
    python3 fix-indents.py --settings <path/to/settings.json> [--dry-run]

Exit codes:
    0  success (or dry-run preview)    1  error
"""

import argparse
import json
import re
import shutil
import sys


def _find_block(content: str, key: str) -> tuple[int, int]:
    """Return (block_start, block_end) char indices of the outermost { } for key."""
    pos = content.index(f'"{key}"')
    block_start = content.index('{', pos)
    depth, block_end = 0, block_start
    for i, ch in enumerate(content[block_start:], block_start):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                block_end = i
                break
    return block_start, block_end


def fix_autoapprove_subkeys(content: str) -> str:
    """Bump approve/matchCommandLine from 6-space to 8-space inside autoApprove block."""
    try:
        bs, be = _find_block(content, "chat.tools.terminal.autoApprove")
    except (ValueError, StopIteration):
        return content  # key absent — skip silently
    block = content[bs:be + 1]
    fixed = re.sub(r'\n      ("approve"|"matchCommandLine")', r'\n        \1', block)
    return content[:bs] + fixed + content[be + 1:]


def fix_files_associations(content: str) -> str:
    """Bump files.associations values from 4-space to 6-space."""
    try:
        bs, be = _find_block(content, "files.associations")
    except (ValueError, StopIteration):
        return content
    block = content[bs:be + 1]
    # level-2 lines inside a 2-space file sit at 4 spaces
    fixed = re.sub(r'\n    ("(?!approve|matchCommandLine))', r'\n      \1', block)
    return content[:bs] + fixed + content[be + 1:]


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore canonical indent overrides.")
    parser.add_argument("--settings", required=True, help="Path to settings.json")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    try:
        content = open(args.settings, encoding="utf-8").read()
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.settings}", file=sys.stderr)
        return 1

    original = content
    content = fix_autoapprove_subkeys(content)
    content = fix_files_associations(content)

    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON invalid after fix: {e}", file=sys.stderr)
        return 1

    if content == original:
        print("No changes needed — indents already correct.")
        return 0

    if args.dry_run:
        changed = sum(1 for a, b in zip(original.splitlines(), content.splitlines()) if a != b)
        print(f"Dry-run: {changed} line(s) would change.")
        return 0

    shutil.copy2(args.settings, args.settings + ".bak")
    open(args.settings, "w", encoding="utf-8").write(content)
    print("Indent overrides applied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
