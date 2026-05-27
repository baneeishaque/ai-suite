#!/usr/bin/env python3
"""Flatten bash backslash-newline continuations into single-line commands.

For each logical command spanning multiple physical lines via a trailing
backslash (`\\`) immediately followed by a newline, join the continuation
lines into a single physical line. Leading whitespace on continuation
lines is collapsed to exactly one space.

Lines NOT part of a `\\<newline>` continuation are preserved verbatim
(including blank lines, comments, and shebangs).
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


CONT_RE = re.compile(r"\\\n[ \t]*")


def flatten_range(lines: list[str], start: int, end: int) -> list[str]:
    """Flatten `\\<newline>` continuations within lines[start-1:end] (1-based inclusive)."""
    n = len(lines)
    if start < 1 or end < start or end > n:
        raise ValueError(f"line range {start}..{end} out of bounds (file has {n} lines)")

    head = "".join(lines[: start - 1])
    body = "".join(lines[start - 1 : end])
    tail = "".join(lines[end:])

    flattened = CONT_RE.sub(" ", body)

    out_text = head + flattened + tail
    return out_text.splitlines(keepends=True)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", required=True, type=Path, help="Path to the bash file to flatten")
    p.add_argument(
        "--line-range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="1-based inclusive line range to flatten (default: whole file)",
    )
    p.add_argument("--dry-run", action="store_true", help="Print result, do not save")
    p.add_argument("--no-backup", action="store_true", help="Skip .bak creation")
    args = p.parse_args()

    if not args.file.is_file():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1

    original = args.file.read_text()
    lines = original.splitlines(keepends=True)

    start, end = (args.line_range if args.line_range else (1, len(lines)))

    try:
        new_lines = flatten_range(lines, start, end)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    new_text = "".join(new_lines)

    if new_text == original:
        print("no changes (no backslash-newline continuations in range)", file=sys.stderr)
        return 0

    if args.dry_run:
        sys.stdout.write(new_text)
        return 0

    if not args.no_backup:
        shutil.copy2(args.file, args.file.with_suffix(args.file.suffix + ".bak"))

    args.file.write_text(new_text)
    print(f"flattened {args.file} (lines {start}..{end})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
