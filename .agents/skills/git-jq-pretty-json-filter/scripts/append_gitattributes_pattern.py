#!/usr/bin/env python3
"""
append_gitattributes_pattern.py — idempotently add a narrow jq-pretty pattern.

Appends a single line of the form:

    <pattern> filter=jq-pretty diff=jq-pretty

to a target .gitattributes file. Refuses dangerously-wide patterns per the
user-mandated narrowness rule (no '**/*.json', no bare '*.json', no '**'
in the leading segment) — those would pull JSONC files (settings.json,
keybindings.json) into jq's strict-JSON parser, which would fail.

Usage:
    append_gitattributes_pattern.py <pattern> [--target .gitattributes]

Exit codes:
    0  appended (or already present)
    2  pattern rejected as too wide
    1  target file write failed
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Reject patterns that match too broadly. The narrowness rule:
#   - must contain at least one literal directory segment, AND
#   - must not start with '**' or '*.', AND
#   - leaf segment may use '*' or '*.json' etc.
REJECT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^\*\*"),                "starts with '**' — too wide"),
    (re.compile(r"^\*\."),                "bare '*.ext' — matches every directory"),
    (re.compile(r"^\*$"),                 "bare '*' — matches everything"),
    (re.compile(r"^[^/]+$"),              "single segment without '/' — too wide"),
]

LINE_SUFFIX = " filter=jq-pretty diff=jq-pretty"


def reject_reason(pattern: str) -> str | None:
    for rx, reason in REJECT_PATTERNS:
        if rx.search(pattern):
            return reason
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pattern", help="Git pathspec / gitattributes pattern (narrow!).")
    ap.add_argument("--target", type=Path, default=Path(".gitattributes"))
    args = ap.parse_args()

    reason = reject_reason(args.pattern)
    if reason:
        print(f"REJECTED: pattern {args.pattern!r} — {reason}", file=sys.stderr)
        print("Acceptable forms include explicit directory + leaf, e.g.:", file=sys.stderr)
        print("  some/dir/*.json", file=sys.stderr)
        print("  a/b/*/specific-name.json", file=sys.stderr)
        return 2

    line = f"{args.pattern}{LINE_SUFFIX}"
    target: Path = args.target

    existing = ""
    if target.exists():
        existing = target.read_text(encoding="utf-8")
        for raw in existing.splitlines():
            if raw.strip() == line:
                print(f"already present: {line}")
                return 0

    try:
        with target.open("a", encoding="utf-8") as f:
            if existing and not existing.endswith("\n"):
                f.write("\n")
            f.write(line + "\n")
    except OSError as e:
        print(f"ERROR: cannot write {target}: {e}", file=sys.stderr)
        return 1

    print(f"appended to {target}: {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
