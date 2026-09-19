#!/usr/bin/env python3
"""fix-list-style.py — Fix MD004: convert asterisk unordered lists to dash style.

Scans for lines that start with `* ` (asterisk-space) used as unordered
list items and converts them to `- ` (dash-space). Only modifies lines
that are actual list items (not emphasis, not inside code blocks).

Usage:
    python3 fix-list-style.py <file.md> [<file.md> ...]

File is modified in-place. Use --check for dry-run.
"""

import argparse
import sys


def fix_file(path: str, dry_run: bool = False) -> bool:
    """Fix asterisk list items. Returns True if changes were made."""
    with open(path, encoding="utf-8") as f:
        original = f.read()

    lines = original.splitlines(keepends=True)
    changed = False
    in_code_fence = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track code fences
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        # Skip non-list lines
        if not stripped.startswith("* ") and stripped != "*":
            continue

        # Check it's really a list item (not emphasis within prose)
        # Emphasis inside a paragraph: ` *text* ` — has content before/after on same line
        # List item: `* text` — starts line
        indent = line[:len(line) - len(line.lstrip())]
        content_after_star = stripped[1:]

        if not content_after_star:
            # Line is just bare "*" on its own — likely a thematic break or empty list item
            continue

        if not content_after_star.startswith(" "):
            # `*text` not `* text` — not a list item
            continue

        old = line
        lines[i] = f"{indent}-{content_after_star}\n"
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
        description="Fix MD004: convert asterisk list items to dash style."
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
