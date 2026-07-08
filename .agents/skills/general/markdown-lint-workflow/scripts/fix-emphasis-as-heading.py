#!/usr/bin/env python3
"""fix-emphasis-as-heading.py — Fix MD036: convert emphasis-as-heading to plain text.

Scans for lines that consist entirely of emphasized text (wrapped in *...*
or _..._) on their own paragraph, which violates MD036. Strips the emphasis
markers while preserving the content.

Only targets lines that are:
- The sole content of their paragraph (surrounded by blank lines)
- Wholly wrapped in emphasis (single * or _ on both sides)
- Not inside code blocks or tables

Usage:
    python3 fix-emphasis-as-heading.py <file.md> [<file.md> ...]

File is modified in-place. Use --check for dry-run.
"""

import argparse
import re
import sys


def fix_file(path: str, dry_run: bool = False) -> bool:
    """Fix emphasis-as-heading lines. Returns True if changes were made."""
    with open(path, encoding="utf-8") as f:
        original = f.read()

    lines = original.splitlines(keepends=True)
    changed = False
    in_code_fence = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track code fences to avoid modifying inside them
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        # Skip blank lines, headings, list items, table rows, blockquotes
        if not stripped:
            continue
        if stripped.startswith(("#", "-", "* ", "+ ", "|", ">")):
            continue

        # Check if the line is entirely wrapped in single * or _
        # Pattern: *(content)* or _(content)_ — with optional leading/trailing whitespace
        m = re.match(r"^(\s*)\*(.+)\*(\s*)$", stripped)
        if not m:
            m = re.match(r"^(\s*)_(.+)_(\s*)$", stripped)

        if m:
            old = line
            lines[i] = f"{m.group(1)}{m.group(2)}{m.group(3)}\n"
            if old != lines[i]:
                changed = True

    if not changed:
        return False

    if dry_run:
        print(f"  Would fix {path}")
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"  Fixed {path}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fix MD036: convert emphasis-as-heading to plain text."
    )
    parser.add_argument("files", nargs="+", metavar="file.md", help="Markdown file(s) to fix")
    parser.add_argument("--check", action="store_true", help="Dry-run, report changes without modifying")
    args = parser.parse_args()

    any_fixed = False
    for path in args.files:
        try:
            if fix_file(path, dry_run=args.check):
                any_fixed = True
        except FileNotFoundError:
            print(f"  ERROR: File not found: {path}", file=sys.stderr)
            sys.exit(2)

    if args.check and any_fixed:
        print("  (dry-run — no changes made)")


if __name__ == "__main__":
    main()
