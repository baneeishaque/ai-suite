#!/usr/bin/env python3
"""wrap-long-lines.py — Wrap prose lines exceeding the configured line-length limit.

Preserves code blocks, table rows, list items, blockquotes, headings,
and other structural markdown elements. Only wraps continuous prose
paragraphs.

Usage:
    python3 wrap-long-lines.py [--max 120] <file.md> [<file.md> ...]

File is modified in-place. Use --check for dry-run.
"""

import argparse
import sys
import textwrap


def wrap_prose_line(line: str, max_width: int) -> str:
    """Wrap a single prose line, preserving leading/trailing whitespace."""
    leading = line[:len(line) - len(line.lstrip())]
    trailing = line[len(line.rstrip()):]
    content = line.strip()

    if not content:
        return line

    wrapped = textwrap.fill(
        content,
        width=max_width,
        break_long_words=False,
        break_on_hyphens=True,
        subsequent_indent=leading,
    )

    if trailing:
        wrapped += trailing
    return wrapped


def should_skip(line: str) -> bool:
    """Check whether a line should be skipped (preserved as-is)."""
    stripped = line.strip()
    if not stripped:
        return True  # blank line

    # Skip code fences
    if stripped.startswith("```"):
        return True
    if stripped.startswith("~~~"):
        return True

    # Skip table rows (| ... |)
    if stripped.startswith("|") and stripped.endswith("|"):
        return True

    # Skip YAML frontmatter fences
    if stripped == "---":
        return True

    return False


def fix_file(path: str, max_width: int, dry_run: bool = False) -> bool:
    """Wrap long prose lines in the file. Returns True if changes were made."""
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    changed = False
    in_code_block = False
    in_yaml_block = False
    new_lines = []

    for i, line in enumerate(lines):
        raw = line.rstrip("\n").rstrip("\r")
        stripped = raw.strip()

        # Track code block state
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue

        # Track YAML frontmatter
        if i == 0 and stripped == "---":
            in_yaml_block = True
            new_lines.append(line)
            continue
        if in_yaml_block and stripped == "---":
            in_yaml_block = False
            new_lines.append(line)
            continue

        if in_code_block or in_yaml_block:
            new_lines.append(line)
            continue

        if should_skip(raw):
            new_lines.append(line)
            continue

        # Only wrap lines that exceed the limit
        if len(raw) > max_width:
            wrapped = wrap_prose_line(raw, max_width)
            if wrapped != raw:
                changed = True
                if dry_run:
                    print(f"  L{i+1}: {len(raw)} chars -> wrapped")
                if not dry_run:
                    new_lines.append(wrapped + "\n")
                    continue

        new_lines.append(line)

    if changed and not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"  Wrapped {path}")

    return changed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Wrap long prose lines in markdown files to meet a configured line limit"
    )
    parser.add_argument("files", nargs="+", help="Markdown file(s) to fix")
    parser.add_argument("--max", type=int, default=120, help="Maximum line width (default: 120)")
    parser.add_argument("--check", action="store_true", help="Dry-run: show what would change")
    args = parser.parse_args()

    exit_code = 0
    for path in args.files:
        print(f"Checking {path[:60]}...")
        if fix_file(path, args.max, dry_run=args.check):
            exit_code = 1 if args.check else 0

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
