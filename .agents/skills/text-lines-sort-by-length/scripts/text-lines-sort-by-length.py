#!/usr/bin/env python3
"""Sort the lines of a text file by physical line length.

Default order is ascending (shortest line first). Sort is stable: ties preserve
the original relative order. An optional `--header-lines N` block is held back
from the sort and re-emitted verbatim at the top, useful for `# filepath:`
markers, shebangs, or other preface lines that must not be reordered.

Lines retain their trailing newline characters during comparison-by-length so
that a missing trailing newline on the last line does not perturb the ordering.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def sort_lines(
    lines: list[str],
    header_lines: int,
    reverse: bool,
    drop_blank: bool,
) -> list[str]:
    if header_lines < 0:
        raise ValueError(f"--header-lines must be >= 0 (got {header_lines})")
    if header_lines > len(lines):
        raise ValueError(
            f"--header-lines {header_lines} exceeds file line count {len(lines)}"
        )

    head = lines[:header_lines]
    body = lines[header_lines:]

    if drop_blank:
        body = [ln for ln in body if ln.strip() != ""]

    # rstrip("\n") so the trailing newline does not contribute to the
    # comparison weight; Python's sort is stable so ties keep original order.
    body_sorted = sorted(body, key=lambda s: len(s.rstrip("\n")), reverse=reverse)

    return head + body_sorted


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", required=True, type=Path, help="Input text file")
    p.add_argument(
        "--output",
        type=Path,
        help="Write sorted output to PATH (default: stdout unless --in-place)",
    )
    p.add_argument(
        "--in-place",
        action="store_true",
        help="Rewrite --file in place (creates .bak unless --no-backup)",
    )
    p.add_argument(
        "--header-lines",
        type=int,
        default=0,
        help="Preserve the first N lines unchanged at the top (default: 0)",
    )
    p.add_argument(
        "--reverse",
        action="store_true",
        help="Sort descending (longest first); default is ascending",
    )
    p.add_argument(
        "--drop-blank",
        action="store_true",
        help="Drop blank lines from the sort body (default: keep them)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print result to stdout regardless of --output/--in-place",
    )
    p.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip .bak creation when --in-place is used",
    )
    args = p.parse_args()

    if not args.file.is_file():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    if args.in_place and args.output:
        print("error: --in-place and --output are mutually exclusive", file=sys.stderr)
        return 1

    original = args.file.read_text()
    lines = original.splitlines(keepends=True)

    try:
        sorted_lines = sort_lines(
            lines,
            header_lines=args.header_lines,
            reverse=args.reverse,
            drop_blank=args.drop_blank,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    out_text = "".join(sorted_lines)
    # Preserve original trailing-newline disposition.
    if original.endswith("\n") and not out_text.endswith("\n"):
        out_text += "\n"

    if args.dry_run:
        sys.stdout.write(out_text)
        return 0

    if args.in_place:
        if not args.no_backup:
            shutil.copy2(args.file, args.file.with_suffix(args.file.suffix + ".bak"))
        args.file.write_text(out_text)
        return 0

    if args.output:
        args.output.write_text(out_text)
        return 0

    sys.stdout.write(out_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
