#!/usr/bin/env python3
"""build-version-superset.py — construct vN+1 as vN verbatim + deltas appended.

Implements the Verbatim-Superset Construction convention
(ai-agent-planning-rules.md §7.1): the new version of a versioned artifact
MUST be the previous version's text kept byte-verbatim, with the new
version's deltas appended — never rewritten, reworded, reordered, or
selectively dropped.

The build is fully deterministic given (--old, --deltas, --change-history-row):
  new_bytes = old_bytes_with_optional_row_insert + b"\\n\\n" + deltas_bytes

--verify recomputes the expected bytes from the same inputs and compares
byte-for-byte, so a build can be proven verbatim-correct at any time.

Tier: 1 (Python 3.12+) — see scripting-language-selection-rules.md §3.
The OLD file is NEVER mutated (read-only input). Refuses to clobber an
existing NEW file unless --overwrite is given.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

CHANGE_HISTORY_RE = re.compile(r"^#{1,6}\s+Change History\s*$")
ROW_RE = re.compile(r"^\s*\|")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def insert_change_history_row(text: str, row: str) -> str:
    """Insert `row` after the last table row of the first Change History section.

    The Change History table is the ONLY sanctioned in-place mutation inside
    the old region: it is the new version's own metadata, not old content.
    A row passed without surrounding pipes is auto-wrapped into a well-formed
    table row (e.g. "ts | summary | rationale" -> "| ts | summary | rationale |").
    Returns the modified text; raises ValueError if no Change History section
    or no table row exists.
    """
    row = row.strip()
    if not row.startswith("|"):
        row = f"| {row} |"
    lines = text.splitlines()
    in_section = False
    last_row_index: int | None = None
    for i, line in enumerate(lines):
        if CHANGE_HISTORY_RE.match(line):
            in_section = True
            continue
        if in_section and ROW_RE.match(line):
            last_row_index = i
            continue
        if in_section and line.strip() == "" and last_row_index is not None:
            in_section = False
    if last_row_index is None:
        raise ValueError("no Change History table row found; cannot stamp row")
    lines.insert(last_row_index + 1, row)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def build_bytes(old_bytes: bytes, deltas_bytes: bytes, row: str | None) -> bytes:
    old_text = old_bytes.decode("utf-8")
    if row is not None:
        old_text = insert_change_history_row(old_text, row)
        old_bytes = old_text.encode("utf-8")
    separator = b"\n\n" if old_bytes and not old_bytes.endswith(b"\n") else b"\n"
    return old_bytes + separator + deltas_bytes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Construct vN+1 of a versioned artifact as vN byte-verbatim + "
            "appended deltas (Verbatim-Superset Construction)."
        )
    )
    parser.add_argument("--old", required=True, help="vN file (read-only; never mutated)")
    parser.add_argument("--new", required=True, help="vN+1 output file to create")
    parser.add_argument("--deltas", required=True, help="markdown deltas block file to append")
    parser.add_argument(
        "--change-history-row",
        help='single row to insert after the last row of the Change History table, e.g. "2026-08-08 | msg | why" '
        "(the only sanctioned edit inside the vN region)",
    )
    parser.add_argument("--overwrite", action="store_true", help="allow writing over an existing --new file")
    parser.add_argument("--dry-run", action="store_true", help="print the build plan; write nothing")
    parser.add_argument("--verify", action="store_true", help="recompute expected bytes and compare byte-for-byte")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    old_path = Path(args.old)
    new_path = Path(args.new)
    deltas_path = Path(args.deltas)

    if not old_path.is_file():
        print(f"error: --old file not found: {old_path}", file=sys.stderr)
        return 2
    if not deltas_path.is_file():
        print(f"error: --deltas file not found: {deltas_path}", file=sys.stderr)
        return 2
    if old_path.resolve() == new_path.resolve():
        print("error: --old and --new must be different files", file=sys.stderr)
        return 2
    if new_path.exists() and not args.overwrite and not args.verify:
        print(f"error: --new already exists (use --overwrite to replace): {new_path}", file=sys.stderr)
        return 2

    old_bytes = old_path.read_bytes()
    deltas_bytes = deltas_path.read_bytes()

    try:
        expected = build_bytes(old_bytes, deltas_bytes, args.change_history_row)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.verify:
        if not new_path.is_file():
            print("error: --verify requires an existing --new file", file=sys.stderr)
            return 2
        actual = new_path.read_bytes()
        ok = actual == expected
        result = {
            "mode": "verify",
            "ok": ok,
            "old": str(old_path),
            "new": str(new_path),
            "old_bytes": len(old_bytes),
            "deltas_bytes": len(deltas_bytes),
            "expected_bytes": len(expected),
            "actual_bytes": len(actual),
            "old_sha256": sha256_hex(old_bytes),
            "expected_sha256": sha256_hex(expected),
            "actual_sha256": sha256_hex(actual),
            "row_inserted": args.change_history_row is not None,
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = "VERBATIM-SUPERSET: OK" if ok else "VERBATIM-SUPERSET: MISMATCH"
            print(f"{status} (old {len(old_bytes)}B -> expected {len(expected)}B, actual {len(actual)}B)")
        return 0 if ok else 1

    if args.dry_run:
        result = {
            "mode": "dry-run",
            "old": str(old_path),
            "new": str(new_path),
            "old_bytes": len(old_bytes),
            "deltas_bytes": len(deltas_bytes),
            "expected_bytes": len(expected),
            "old_sha256": sha256_hex(old_bytes),
            "expected_sha256": sha256_hex(expected),
            "row_inserted": args.change_history_row is not None,
            "would_overwrite": new_path.exists(),
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(
                f"dry-run: {old_path.name} ({len(old_bytes)}B) -> {new_path.name} "
                f"({len(expected)}B) with {len(deltas_bytes)}B deltas appended"
                f"{' + change-history row' if args.change_history_row else ''}"
            )
        return 0

    new_path.write_bytes(expected)
    result = {
        "mode": "build",
        "old": str(old_path),
        "new": str(new_path),
        "old_bytes": len(old_bytes),
        "deltas_bytes": len(deltas_bytes),
        "new_bytes": len(expected),
        "old_sha256": sha256_hex(old_bytes),
        "new_sha256": sha256_hex(expected),
        "row_inserted": args.change_history_row is not None,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"built {new_path.name}: {len(old_bytes)}B verbatim old + "
            f"{len(deltas_bytes)}B deltas = {len(expected)}B"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
