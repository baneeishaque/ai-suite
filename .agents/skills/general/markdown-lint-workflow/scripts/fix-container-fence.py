#!/usr/bin/env python3
"""fix-container-fence.py — Add language tag to container fences.

Container fences are fenced code blocks whose outer fence uses 4+ backtick
markers to wrap content that itself contains ``` fences — the standard
markdown pattern for showing markdown syntax examples.

This script detects such blocks and adds a ``text`` language tag to the
opening fence marker, satisfying MD040 while leaving the block as a fenced
code block (MD046-compliant). The inner ``` fences render literally inside
the outer fence.

Container fences are distinct from normal bare fences (handled by the sibling
fix-fenced-code-language.py): they wrap markdown-syntax examples, not code.

Usage:
    python3 fix-container-fence.py <file.md> [<file.md> ...]

File is modified in-place. Use --check for dry-run.
"""

import argparse
import re
import sys


FENCE_RE = re.compile(r"^(?P<mark>`{3,})\s*$")


def fence_marker(stripped: str) -> str:
    m = FENCE_RE.match(stripped)
    return m.group("mark") if m else ""


def fix_file(path: str, dry_run: bool = False) -> bool:
    """Add language tag to container fences. Returns True if changes were made."""
    with open(path, encoding="utf-8") as f:
        original = f.read()

    lines = original.splitlines(keepends=True)

    # Collect candidate blocks for processing bottom-up
    blocks: list[tuple[int, int, str, list[int]]] = []

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        # Look for a container-fence opening: 4+ backticks, no language
        marker = fence_marker(stripped)
        if marker and len(marker) >= 4:
            open_idx = i
            content_indices: list[int] = []
            i += 1
            while i < len(lines):
                inner_stripped = lines[i].strip()
                inner_marker = fence_marker(inner_stripped)
                if inner_marker == marker:
                    blocks.append((open_idx, i, marker, content_indices))
                    i += 1
                    break
                content_indices.append(i)
                i += 1
            else:
                pass
        else:
            i += 1

    # Filter: only blocks whose content contains inner ``` fences
    targets: list[tuple[int, int, str]] = []
    for open_idx, close_idx, marker, content_indices in blocks:
        has_inner_fence = False
        for ci in content_indices:
            inner_stripped = lines[ci].strip()
            if inner_stripped.startswith("```"):
                has_inner_fence = True
                break
        if has_inner_fence:
            targets.append((open_idx, close_idx, marker))

    if not targets:
        return False

    if dry_run:
        for open_idx, close_idx, _ in targets:
            print(f"  Would fix {path}:{open_idx + 1}")
        return False

    # Process targets bottom-up to preserve line indices
    for open_idx, close_idx, marker in reversed(targets):
        line = lines[open_idx]
        indent = line[: len(line) - len(line.lstrip())]
        lines[open_idx] = f"{indent}{marker}text\n"

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    for open_idx, close_idx, tmarker in targets:
        print(f"  Fixed {path}:{open_idx + 1}  ({tmarker} -> {tmarker}text)")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add language tag to container fences (4+ backtick with inner ```)."
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
