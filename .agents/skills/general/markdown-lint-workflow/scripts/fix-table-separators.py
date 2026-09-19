#!/usr/bin/env python3
"""fix-table-separators.py — Fix MD060 compact-style table separators.

Replaces compact separator rows like |---|---| with properly spaced
| --- | --- | style to satisfy markdownlint-cli2 MD060.

Usage:
    python3 fix-table-separators.py <file.md> [<file.md> ...]

File is modified in-place. Use --check for dry-run.
"""

import argparse
import sys


def is_separator_row(stripped: str) -> bool:
    """True if the line looks like a table separator (only | - : and spaces)."""
    return (stripped.startswith("|") and stripped.endswith("|")
            and all(c in "|-: " for c in stripped.strip("|")))


def is_compact_separator(stripped: str) -> bool:
    """True if the separator uses compact style (no spaces around dashes)."""
    return (" --- " not in stripped and " :--- " not in stripped
            and " ---: " not in stripped and " :--: " not in stripped)


def fix_separator(row: str) -> str:
    """Convert a compact separator to properly spaced form."""
    parts = row.strip("|").split("|")
    spaced = " | ".join(p.strip() for p in parts)
    return f"| {spaced} |"


def fix_file(path: str, dry_run: bool = False) -> bool:
    """Fix all compact table separator rows. Returns True if changes were made."""
    with open(path, encoding="utf-8") as f:
        original = f.read()

    changed = False
    out_lines = []

    for i, line in enumerate(original.split("\n")):
        stripped = line.strip()
        if is_separator_row(stripped) and is_compact_separator(stripped):
            fixed = fix_separator(stripped)
            if fixed != stripped:
                changed = True
                if dry_run:
                    print(f"  L{i+1}: {stripped} -> {fixed}")
                else:
                    indent = line[:len(line) - len(line.lstrip())]
                    out_lines.append(indent + fixed)
                continue
        out_lines.append(line)

    if changed and not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(out_lines))
        print(f"  Fixed {path}")

    return changed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fix MD060 compact-style table separators in markdown files"
    )
    parser.add_argument("files", nargs="+", help="Markdown file(s) to fix")
    parser.add_argument("--check", action="store_true", help="Dry-run: show what would change")
    args = parser.parse_args()

    exit_code = 0
    for path in args.files:
        print(f"Checking {path}...")
        if fix_file(path, dry_run=args.check):
            exit_code = 1 if args.check else 0

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
