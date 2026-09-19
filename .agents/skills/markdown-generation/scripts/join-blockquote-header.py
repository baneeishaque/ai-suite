#!/usr/bin/env python3
"""join-blockquote-header.py — normalize metadata-header blockquote runs in markdown.

Rendering problem addressed
---------------------------
GitHub/CommonMark blockquotes collapse consecutive ``> **Label:**`` lines into a
single paragraph. The ai-suite skill-library convention fixes this by appending
``<br>`` to every header line except the last line of the run, so each label
renders on its own visual line.

This script owns that convention generically:

  - a header line matches ``^>\s*\*\*[^*\n]+\*\*`` (blockquote ``>``, then a
    closed bold token ``**...**`` whose content is a label)
  - consecutive matching lines form a run; a run of 1 line is left untouched
  - within a run of 2+ lines every line but the last gets a trailing ``<br>``
  - a trailing ``<br>`` already present on the run's LAST line is stripped, so
    the canonical shape is idempotent (a second run changes nothing)

Modes (mutually exclusive)
--------------------------
  default      : normalized text to stdout (feed via stdin or a file argument)
  --check      : exit 0 when input is already canonical, 1 when changes are
                 needed (no output changes)
  --apply      : rewrite the file in place, only when a change is needed
  --diff       : unified diff of the change (stdout)

Behavior guarantees
-------------------
  - line endings (LF / CRLF) of every untouched line are preserved byte-for-byte
  - a missing final newline stays missing
  - non-header lines are untouched
  - idempotent: ``transform(transform(x)) == transform(x)``
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

HEADER_RE = re.compile(r"^>\s*\*\*[^*\n]+\*\*")


def strip_eol(line: str) -> tuple[str, str]:
    """Split a line into (content, eol) where eol is '', '\\n', or '\\r\\n'."""
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def is_header_line(line: str) -> bool:
    body, _eol = strip_eol(line)
    return bool(HEADER_RE.match(body))


def canonical_line(body: str, eol: str, is_last: bool) -> str:
    body = body.rstrip()
    if body.endswith("<br>"):
        body = body[: -len("<br>")]
    if not is_last:
        body = body + "<br>"
    return body + eol


def transform(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        if not is_header_line(lines[i]):
            out.append(lines[i])
            i += 1
            continue
        j = i
        while j < n and is_header_line(lines[j]):
            j += 1
        run = lines[i:j]
        if len(run) < 2:
            out.extend(run)
        else:
            for k, line in enumerate(run):
                body, eol = strip_eol(line)
                out.append(canonical_line(body, eol, k == len(run) - 1))
        i = j
    return "".join(out)


def read_input(path: str | None) -> tuple[str, str]:
    if path is None or path == "-":
        return sys.stdin.read(), "-"
    p = Path(path)
    if not p.is_file():
        sys.exit(f"error: no such file: {path}")
    return p.read_text(encoding="utf-8"), path


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("path", nargs="?", default=None, help="file to process (default: stdin)")
    ap.add_argument("--check", action="store_true", help="exit 1 when changes would be needed")
    ap.add_argument("--apply", action="store_true", help="rewrite the file in place when needed")
    ap.add_argument("--diff", action="store_true", help="print a unified diff of the change")
    args = ap.parse_args()

    if args.apply and (args.path is None or args.path == "-"):
        ap.error("--apply requires a file argument (stdin cannot be rewritten)")

    text, name = read_input(args.path)
    result = transform(text)

    if args.check:
        if result == text:
            print(f"[join-blockquote-header] clean: {name}")
            return 0
        print(f"[join-blockquote-header] changes needed: {name}")
        return 1

    if args.diff:
        if result == text:
            print(f"[join-blockquote-header] clean: {name}")
            return 0
        from_lines = text.splitlines(keepends=True)
        to_lines = result.splitlines(keepends=True)
        sys.stdout.writelines(
            difflib.unified_diff(
                from_lines, to_lines, fromfile=name, tofile=f"{name} (normalized)"
            )
        )
        return 1

    if args.apply:
        if result == text:
            print(f"[join-blockquote-header] unchanged: {name}")
            return 0
        Path(name).write_text(result, encoding="utf-8")
        print(f"[join-blockquote-header] applied: {name}")
        return 0

    sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())