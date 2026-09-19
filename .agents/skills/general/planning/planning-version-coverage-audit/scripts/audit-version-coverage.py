#!/usr/bin/env python3
"""audit-version-coverage.py — literal section-by-section coverage audit.

Compares two versions of the SAME markdown artifact and reports, per
section of the OLD document, whether the NEW document covers / enhances /
drops it. Emits a deterministic FULL / PARTIAL / MISSING verdict.

Tier: 1 (Python 3.12+) — see scripting-language-selection-rules.md §3.
Read-only; never mutates its inputs.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECTION_RE = re.compile(r"^(#{2,6})\s+(.*)$")

COVERED = "COVERED"
ENHANCED = "ENHANCED"
DROPPED = "DROPPED"


def normalize_heading(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).lower()


def normalize_body(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).strip()


def parse_sections(text: str, heading_filter: re.Pattern[str]) -> list[dict]:
    """Split doc into sections: heading text, level, and body until next heading."""
    sections: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    body_lines: list[str] = []

    def flush() -> None:
        nonlocal current, body_lines
        if current is not None:
            current["body"] = normalize_body("\n".join(body_lines))
            sections.append(current)
        current = None
        body_lines = []

    for line in text.splitlines():
        m = SECTION_RE.match(line)
        if m:
            flush()
            heading = m.group(2).strip()
            if heading_filter.search(m.group(0)):
                current = {"heading": heading, "norm": normalize_heading(heading), "body": ""}
        elif current is not None:
            body_lines.append(line)
    flush()
    return sections


def classify_old(old: dict[str, object], new_sections: list[dict[str, object]]) -> dict[str, object]:
    head = old.get("norm", "")
    old_body = str(old.get("body", ""))
    for new in new_sections:
        if new.get("norm") == head:
            new_body = str(new.get("body", ""))
            if old_body in new_body:
                classification = ENHANCED if len(new_body) > len(old_body) else COVERED
                return {
                    "old_heading": old.get("heading"),
                    "class": classification,
                    "new_heading": new.get("heading"),
                }
            # same heading but body not a superset — try the next duplicate heading
            # before declaring DROPPED (duplicate headings with stubs like "(see top)")
    return {"old_heading": old.get("heading"), "class": DROPPED, "new_heading": None}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--old", required=True, help="old artifact path (vN)")
    ap.add_argument("--new", required=True, help="new artifact path (vN+1)")
    ap.add_argument("--json", action="store_true", help="machine-readable JSON output")
    ap.add_argument("--headings", default=r"^##\s|^###\s", help="regex matching headings to audit (default ## and ###)")
    args = ap.parse_args()

    old_path = Path(args.old)
    new_path = Path(args.new)

    if not old_path.is_file():
        print(json.dumps({"error": f"old file not found: {old_path}"}) if args.json else f"error: old file not found: {old_path}")
        return 1
    if not new_path.is_file():
        print(json.dumps({"error": f"new file not found: {new_path}"}) if args.json else f"error: new file not found: {new_path}")
        return 1

    try:
        heading_filter = re.compile(args.headings)
    except re.error as exc:
        print(f"usage error: bad --headings regex: {exc}")
        return 2

    old_text = old_path.read_text(encoding="utf-8", errors="replace")
    new_text = new_path.read_text(encoding="utf-8", errors="replace")

    old_sections = parse_sections(old_text, heading_filter)
    new_sections = parse_sections(new_text, heading_filter)

    rows = [classify_old(old, new_sections) for old in old_sections]
    dropped = [r for r in rows if r["class"] == DROPPED]
    verdict = "FULL" if not dropped else "PARTIAL"
    if not old_sections:
        verdict = "MISSING"

    result = {
        "old": str(old_path),
        "new": str(new_path),
        "old_sections": len(old_sections),
        "new_sections": len(new_sections),
        "verdict": verdict,
        "rows": rows,
    }

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"old_sections={result['old_sections']} new_sections={result['new_sections']} verdict={verdict}")
        for r in rows:
            print(f"{r['class']:8} {r.get('old_heading', '')} -> {r.get('new_heading', 'NO MATCH')}")

    return 0 if verdict == "FULL" else 1


if __name__ == "__main__":
    sys.exit(main())