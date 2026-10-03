# !/usr/bin/env python3
"""write-drop-todo.py — rewrite a git rebase todo file to drop or edit named commits.

Used as GIT_SEQUENCE_EDITOR: git passes the rebase todo file path as the last
argument (direct callers may pass it first — the script resolves whichever
positional exists as a file to be the todo). Rewrites every `pick <sha> ...`
line whose SHA is in the target set
to `drop <sha>` (default) or `edit <sha>` (--edit; edit wins when a SHA is in
both sets). SHA matching is prefix-tolerant — the todo file usually carries
abbreviated SHAs while callers pass full ones — and a todo SHA that matches
more than one distinct target aborts with an ambiguity error before any write.
Idempotent — lines already in the target state are left untouched, and every
other line is preserved byte-exact (comments, blanks, reword/squash/fixup
actions, CRLF/LF endings).

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
_HEX_TOKEN_RE = re.compile(r"[0-9a-fA-F]{7,40}")

def validate_shas(values: list[str]) -> set[str]:
    bad = [v for v in values if not _SHA_RE.fullmatch(v)]
    if bad:
        raise ValueError(f"invalid commit SHA(s): {', '.join(bad)}")
    return {v.lower() for v in values}

def _matches(todo_sha: str, target: str) -> bool:
    """Prefix-tolerant SHA match: either side may be the abbreviation."""
    t = target.lower()
    s = todo_sha.lower()
    return t.startswith(s) or s.startswith(t)

def rewrite_todo(lines: list[bytes], drop: set[str], edit: set[str]) -> list[bytes]:
    out: list[bytes] = []
    for line in lines:
        text = line.decode("utf-8", errors="surrogateescape")
        match = _PICK_RE.match(text)
        if not match:
            out.append(line)
            continue
        sha = match.group("sha").lower()
        matched_drop = [t for t in drop if _matches(sha, t)]
        matched_edit = [t for t in edit if _matches(sha, t)]
        unique: list[str] = []
        for target in sorted(set(matched_drop) | set(matched_edit)):
            if not any(_matches(target, seen) for seen in unique):
                unique.append(target)
        if not unique:
            out.append(line)
            continue
        if len(unique) > 1:
            raise ValueError(
                f"ambiguous abbreviation {sha} matches multiple targets: {', '.join(unique)}"
            )
        action = "edit" if matched_edit else "drop"
        rewritten = text[: match.start("action")] + action + text[match.end("action"):]
        out.append(rewritten.encode("utf-8", errors="surrogateescape"))
    return out

def check_presence(data: bytes, targets: set[str]) -> list[str]:
    text = data.decode("utf-8", errors="surrogateescape")
    tokens = [m.group(0).lower() for m in _HEX_TOKEN_RE.finditer(text)]
    return [
        target
        for target in sorted(targets)
        if not any(_matches(token, target) for token in tokens)
    ]

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rewrite a git rebase todo file: pick -> drop/edit for named SHAs."
    )
    parser.add_argument(
        "items", nargs="+", metavar="ITEM",
        help="Commit SHAs plus the rebase todo file (git appends the todo "
             "path last; direct callers may pass it first).",
    )
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
    args = parser.parse_intermixed_args()

    tokens = args.items
    if Path(tokens[0]).is_file() and len(tokens) >= 2:
        todo_path, sha_tokens = tokens[0], tokens[1:]
    else:
        todo_path, sha_tokens = tokens[-1], tokens[:-1]
    if not sha_tokens:
        print("write-drop-todo: no commit SHAs given", file=sys.stderr)
        return 2

    try:
        drop_targets = validate_shas(sha_tokens)
        edit_targets = validate_shas(args.edit)
    except ValueError as error:
        print(f"write-drop-todo: {error}", file=sys.stderr)
        return 2

    targets = drop_targets | edit_targets
    todo = Path(todo_path)
    if not todo.is_file():
        print(f"write-drop-todo: todo file not found: {todo_path}", file=sys.stderr)
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
    try:
        rewritten = rewrite_todo(lines, drop_targets, edit_targets)
    except ValueError as error:
        print(f"write-drop-todo: {error}", file=sys.stderr)
        return 1

    if args.dry_run:
        sys.stdout.buffer.write(b"".join(rewritten))
        return 0

    todo.write_bytes(b"".join(rewritten))
    return 0

if __name__ == "__main__":
    sys.exit(main())
