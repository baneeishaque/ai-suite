# !/usr/bin/env python3
"""write-drop-todo.py — rewrite a git rebase todo file to drop or edit named commits.

Used as GIT_SEQUENCE_EDITOR: git passes the rebase todo file path as the last
argument. Rewrites every `pick <sha> ...` line whose SHA is in the target set
to `drop <sha>` (default) or `edit <sha>` (--edit). Idempotent — lines already
in the target state are left untouched, and every other line is preserved
byte-exact (comments, blanks, reword/squash/fixup actions, CRLF/LF endings).

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §3 —
subprocess-free pure text transform, stdlib only.

Exit codes:
  0  success
  1  --check failure (target SHA absent from the todo file) or validation error
  2  usage error
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_PICK_RE = re.compile(
    r"^(?P<action>pick|p)(?P<sep>[ \t]+)(?P<sha>[0-9a-fA-F]{7,40})(?P<rest>.*)$"
)
_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")

def validate_shas(values: list[str]) -> set[str]:
    bad = [v for v in values if not_SHA_RE.fullmatch(v)]
    if bad:
        raise ValueError(f"invalid commit SHA(s): {', '.join(bad)}")
    return {v.lower() for v in values}

def rewrite_todo(lines: list[bytes], drop: set[str], edit: set[str]) -> list[bytes]:
    out: list[bytes] = []
    for line in lines:
        text = line.decode("utf-8", errors="surrogateescape")
        match =_PICK_RE.match(text)
        if not match:
            out.append(line)
            continue
        sha = match.group("sha").lower()
        if sha not in drop and sha not in edit:
            out.append(line)
            continue
        action = "drop" if sha in drop else "edit"
        rewritten = text[: match.start("action")] + action + text[match.end("action"):]
        out.append(rewritten.encode("utf-8", errors="surrogateescape"))
    return out

def check_presence(data: bytes, targets: set[str]) -> list[str]:
    text = data.decode("utf-8", errors="surrogateescape")
    return [sha for sha in sorted(targets) if not re.search(rf"\b{re.escape(sha)}\b", text)]

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rewrite a git rebase todo file: pick -> drop/edit for named SHAs."
    )
    parser.add_argument("todo_file", help="Path to the rebase todo file (git passes it last).")
    parser.add_argument("shas", nargs="+", help="Commit SHAs to drop or edit.")
    parser.add_argument(
        "--edit", action="append", default=[], metavar="SHA",
        help="Instead of drop, rewrite pick -> edit for this SHA (repeatable).",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Do not write; exit 1 if any target SHA is absent from the todo file.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the rewritten todo to stdout; do not modify the file.",
    )
    args = parser.parse_args()

    try:
        drop_targets = validate_shas(args.shas)
        edit_targets = validate_shas(args.edit)
    except ValueError as error:
        print(f"write-drop-todo: {error}", file=sys.stderr)
        return 2

    targets = drop_targets | edit_targets
    todo = Path(args.todo_file)
    if not todo.is_file():
        print(f"write-drop-todo: todo file not found: {args.todo_file}", file=sys.stderr)
        return 2

    data = todo.read_bytes()

    missing = check_presence(data, targets)
    if args.check:
        if missing:
            for sha in missing:
                print(f"write-drop-todo: --check failure: {sha} absent from todo file", file=sys.stderr)
            return 1
        return 0

    lines = data.splitlines(keepends=True)
    rewritten = rewrite_todo(lines, drop_targets, edit_targets)

    if args.dry_run:
        sys.stdout.buffer.write(b"".join(rewritten))
        return 0

    todo.write_bytes(b"".join(rewritten))
    return 0

if __name__ == "__main__":
    sys.exit(main())
