#!/usr/bin/env python3
"""fix-fenced-code-language.py — Fix MD040: add language specifier to fenced code blocks.

Properly handles opening vs closing fences with state tracking:

- Opening fence with language (```typescript) → leave as-is, enter fence state
- Opening fence without language (```) → add default language, enter fence state
- Closing fence without language (``` while in fence) → leave as-is, exit fence state
- Closing fence WITH language (```text while in fence) → strip language (fix --fix damage), exit fence state

Usage:
    python3 fix-fenced-code-language.py [--default text] <file.md> [<file.md> ...]

File is modified in-place. Use --check for dry-run.
"""

import argparse
import re
import sys


def fix_file(path: str, default_lang: str = "text", dry_run: bool = False) -> bool:
    """Fix fenced code blocks. Returns True if changes were made."""
    with open(path, encoding="utf-8") as f:
        original = f.read()

    lines = original.splitlines(keepends=True)
    changed = False
    in_fence = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip blank lines inside fences (content)
        if in_fence and not stripped.startswith("```"):
            continue

        # Skip blank lines outside fences
        if not stripped or stripped.startswith("#"):
            continue

        # Detect fence lines (start with ```)
        if not stripped.startswith("```"):
            continue

        # --- State: inside a fence ---
        if in_fence:
            # This is a CLOSING fence
            if stripped != "```":
                # Fence has a language tag — strip it (likely --fix damage)
                indent = line[:len(line) - len(line.lstrip())]
                old = line
                lines[i] = f"{indent}```\n"
                if old != lines[i]:
                    changed = True
            in_fence = False
            continue

        # --- State: outside a fence ---
        # This is an OPENING fence
        if stripped == "```":
            # Bare opening fence — add default language
            indent = line[:len(line) - len(line.lstrip())]
            old = line
            lines[i] = f"{indent}```{default_lang}\n"
            if old != lines[i]:
                changed = True
        # else: already has language, leave as-is
        in_fence = True

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
        description="Fix MD040: add/remove language specifier from fenced code blocks."
    )
    parser.add_argument("files", nargs="+", metavar="file.md", help="Markdown file(s) to fix")
    parser.add_argument("--default", default="text", help="Default language to add (default: text)")
    parser.add_argument("--check", action="store_true", help="Dry-run, report changes without modifying")
    args = parser.parse_args()

    any_fixed = False
    for path in args.files:
        try:
            if fix_file(path, args.default, dry_run=args.check):
                any_fixed = True
        except FileNotFoundError:
            print(f"  ERROR: File not found: {path}", file=sys.stderr)
            sys.exit(2)

    if args.check and any_fixed:
        print("  (dry-run — no changes made)")


if __name__ == "__main__":
    main()
