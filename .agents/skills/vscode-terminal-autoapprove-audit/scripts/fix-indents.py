#!/usr/bin/env python3
"""
fix-indents.py — Normalize a VS Code settings.json to the canonical 4-space indent.

Part of the vscode-terminal-autoapprove-audit skill.
See ../SKILL.md §3.1 for the formatting contract.

Run this after ANY edit that rewrites the file (edit-entry.py, audit-autoapprove.py,
or a manual json.dump call with a different indent).

Canonical convention (as of May 2026):
    Plain 4-space-per-level JSON throughout — no per-key overrides.
    Equivalent to `json.dumps(data, indent=4, ensure_ascii=False)`.

Usage:
    python3 fix-indents.py --settings <path/to/settings.json> [--dry-run]

Exit codes:
    0  success (or dry-run preview)    1  error
"""

import argparse
import json
import shutil
import sys


def normalize(content: str) -> str:
    data = json.loads(content)
    return json.dumps(data, indent=4, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize settings.json to 4-space indent.")
    parser.add_argument("--settings", required=True, help="Path to settings.json")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    try:
        original = open(args.settings, encoding="utf-8").read()
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.settings}", file=sys.stderr)
        return 1

    try:
        content = normalize(original)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON invalid: {e}", file=sys.stderr)
        return 1

    if content == original:
        print("No changes needed — indents already canonical (4-space).")
        return 0

    if args.dry_run:
        changed = sum(1 for a, b in zip(original.splitlines(), content.splitlines()) if a != b)
        print(f"Dry-run: {changed} line(s) would change.")
        return 0

    shutil.copy2(args.settings, args.settings + ".bak")
    open(args.settings, "w", encoding="utf-8").write(content)
    print("Indents normalized to 4-space.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
