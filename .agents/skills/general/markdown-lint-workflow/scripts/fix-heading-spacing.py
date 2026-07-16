#!/usr/bin/env python3
"""fix-heading-spacing.py — Fix MD022: ensure blank line before headings.

Scans for heading lines (starting with #) that don't have a blank line
before them and inserts one. Skips the first line of the file and headings
inside code blocks.

Usage:
    python3 fix-heading-spacing.py <file.md> [<file.md> ...]

File is modified in-place. Use --check for dry-run.
"""

import argparse
import sys


def fix_file(path: str, dry_run: bool = False) -> bool:
    """Fix heading spacing. Returns True if changes were made."""
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

        # Skip non-heading lines and first line
        if i == 0 or not stripped.startswith("#"):
            continue

        # Check if previous line is not blank
        prev = lines[i - 1].strip()
        if prev != "":
            old = line
            lines[i] = f"\n{line}"
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
        description="Fix MD022: ensure blank line before headings."
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
