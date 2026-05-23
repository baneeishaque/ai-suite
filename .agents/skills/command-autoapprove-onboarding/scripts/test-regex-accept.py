#!/usr/bin/env python3
"""
test-regex-accept.py — Regex acceptance harness for autoApprove entries.

Validates that a candidate `chat.tools.terminal.autoApprove` regex key
matches every command in a MUST-MATCH list and rejects every command in
a MUST-REJECT list. Mandated by SKILL.md §5.1 (safe-chain entries) and
recommended for all non-trivial §5 entries.

Usage
-----
1. Inline (quickest, for the agent during onboarding):

       python test-regex-accept.py --pattern '^git status( [^;&|<>$`()]+)*$' \
           --match 'git status' --match 'git status --porcelain' \
           --reject 'git status; rm -rf ~' --reject 'git status && echo x'

2. From a spec file (for repeatable suites — commit alongside the entry):

       python test-regex-accept.py --spec my-entry.spec.json

   spec.json shape:
       {
         "pattern": "^...$",
         "must_match":  ["...", "..."],
         "must_reject": ["...", "..."]
       }

Exit code 0 == all assertions held; 1 == one or more failures.
The `pattern` is interpreted as a Python `re` pattern (no surrounding
`/.../` slashes — strip those from the settings.json key).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def run(pattern: str, must_match: list[str], must_reject: list[str]) -> int:
    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        print(f"FATAL: pattern does not compile: {exc}", file=sys.stderr)
        return 2
    failures = 0
    for cmd in must_match:
        ok = compiled.match(cmd) is not None
        mark = "OK  " if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"{mark}  expect=match   got={'match' if ok else 'no':5s}  :: {cmd!r}")
    for cmd in must_reject:
        ok = compiled.match(cmd) is None
        mark = "OK  " if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"{mark}  expect=reject  got={'reject' if ok else 'match':5s} :: {cmd!r}")
    print(f"\n{failures} failure(s); {len(must_match) + len(must_reject)} total")
    return 0 if failures == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", type=Path, help="JSON spec file with pattern/must_match/must_reject")
    ap.add_argument("--pattern", help="Inline regex pattern (strip leading/trailing /)")
    ap.add_argument("--match", action="append", default=[], help="String that MUST match (repeatable)")
    ap.add_argument("--reject", action="append", default=[], help="String that MUST reject (repeatable)")
    args = ap.parse_args()

    if args.spec:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        return run(spec["pattern"], spec.get("must_match", []), spec.get("must_reject", []))
    if not args.pattern:
        ap.error("either --spec or --pattern is required")
    return run(args.pattern, args.match, args.reject)


if __name__ == "__main__":
    sys.exit(main())
