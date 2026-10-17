#!/usr/bin/env python3
"""Detect whether a topic already has an owning skill, or is only MENTIONED.

A hand-rolled `grep` over `.agents/skills/**/SKILL.md` treats a prose mention as
an owner, which is exactly the failure that parks a new section in the wrong
skill: a skill that discusses a topic is not the skill that OWNS it.

Ownership test: a skill owns a topic when the phrase appears inside its declared
scope -- the frontmatter `description`, the Description blockquote under the
title, or its `## Composition Rationale` section. A phrase found only in body
prose is a MENTION.

Tier: Tier 1 (Python) per scripting-language-selection-rules.md section 3 (Tier 1
is the default) and section 4 (section parsing + JSON verdict assembly) -- stdlib
only, no CPU bottleneck, no ecosystem mandate.

Read-only contract: reads SKILL.md files, writes nothing except stdout JSON.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

DESCRIPTION_HEADINGS = ("description", "## description")
SCOPE_SECTIONS = ("composition rationale",)


def _sections(text: str):
    """Split a SKILL.md into (heading, body) pairs, headings lowercased."""
    lines = text.splitlines()
    out = []
    current = ""
    buf = []
    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            out.append((current, "\n".join(buf)))
            current = m.group(2).strip().lower()
            buf = []
        else:
            buf.append(line)
    out.append((current, "\n".join(buf)))
    return out


def _frontmatter_description(text: str) -> str:
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    block = parts[1].lower()
    m = re.search(r"^description:\s*(.*)$", block, re.M)
    return m.group(1) if m else ""


def classify(path: pathlib.Path, needle: str) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    low = text.lower()
    if needle not in low:
        return {}
    skill = path.parent.name
    scope_hits = []
    mention_lines = []

    if needle in _frontmatter_description(text):
        scope_hits.append("frontmatter description")

    for heading, body in _sections(text):
        if needle not in body.lower():
            continue
        if any(heading == s or heading.startswith(s) for s in SCOPE_SECTIONS):
            scope_hits.append(f"section '{heading}'")
        elif heading in DESCRIPTION_HEADINGS:
            scope_hits.append(f"section '{heading}'")
        else:
            for n, line in enumerate(body.splitlines(), start=1):
                if needle in line.lower():
                    mention_lines.append(n)

    return {
        "skill": skill,
        "path": str(path),
        "classification": "OWNER" if scope_hits else "MENTION",
        "scope_evidence": scope_hits,
        "first_mention_lines": mention_lines[:3],
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Detect whether a topic has an owning skill or is only mentioned."
    )
    ap.add_argument("--topic", required=True, help="2-3 word topic phrase to test for.")
    ap.add_argument(
        "--skills-dir",
        default=".agents/skills",
        help="Skills root to scan (default: .agents/skills).",
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON (default is JSON).")
    args = ap.parse_args()

    words = args.topic.lower().split()
    if not (2 <= len(words) <= 3):
        sys.stderr.write("error: --topic must be a 2-3 word phrase\n")
        return 2

    root = pathlib.Path(args.skills_dir)
    if not root.is_dir():
        sys.stderr.write("error: skills dir not found: %s\n" % root)
        return 2

    needle = " ".join(words)
    results = []
    for skill_md in sorted(root.rglob("SKILL.md")):
        found = classify(skill_md, needle)
        if found:
            results.append(found)

    owners = [r for r in results if r["classification"] == "OWNER"]
    mentions = [r for r in results if r["classification"] == "MENTION"]

    payload = {
        "topic": needle,
        "skills_scanned": len(list(root.rglob("SKILL.md"))),
        "owners": owners,
        "mentions": mentions,
        "verdict": "OWNER_EXISTS" if owners else "NO_OWNER_CREATE",
        "action": (
            "enrich the owning skill - do NOT add a parallel one"
            if owners
            else "no owner exists: create a new skill, or extend the closest existing owner"
        ),
    }
    print(json.dumps(payload, indent=2))
    return 1 if owners else 0


if __name__ == "__main__":
    sys.exit(main())