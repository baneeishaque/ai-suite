#!/usr/bin/env python3
"""Suggest which existing skills should link INBOUND to a newly created skill.

`AGENTS-legacy.md` registration makes a skill discoverable; it does not connect
it to the skills whose workflows it serves. A rename gets an inbound sweep (see
skill-factory 5.1); a CREATION did not, which is how a new base ships with no
consumer pointing at it.

This script cannot decide the answer - judgement is required - but it can make the
candidate set mechanical and complete. It reports two lists:

  reverse_links    existing skills that already link TO the new skill (the
                   bidirectional contract, per skill-factory 2.5 / 5.2.1)
  candidates       existing skills whose text already matches the new skill's
                   probe terms, i.e. workflows that plausibly need the pointer

Probe terms default to the content words of the new skill's frontmatter
description, minus stopwords. Override with repeatable --probe when the
description wording does not predict the consumers.

Tier: Tier 1 (Python) per scripting-language-selection-rules.md section 3 (Tier 1
is the default) and section 4 (term scoring + JSON report assembly) -- stdlib
only, no CPU bottleneck, no ecosystem mandate.

Read-only contract: reads SKILL.md files, writes nothing except stdout JSON.
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into",
    "is", "it", "its", "of", "on", "or", "that", "the", "then", "this", "to",
    "via", "was", "were", "when", "with", "you", "your",
}

MIN_TERM_LEN = 5


def _frontmatter_description(text: str) -> str:
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    m = re.search(r"^description:\s*(.*)$", parts[1], re.M)
    return m.group(1) if m else ""


def derive_probes(new_skill_md: pathlib.Path) -> list:
    text = new_skill_md.read_text(encoding="utf-8", errors="replace")
    desc = _frontmatter_description(text)
    words = re.findall(r"[a-z0-9][a-z0-9-]{%d,}" % (MIN_TERM_LEN - 2), desc.lower())
    seen = []
    for w in words:
        w = w.strip("-")
        if len(w) >= MIN_TERM_LEN and w not in STOPWORDS and w not in seen:
            seen.append(w)
    return seen


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Suggest inbound reference sources for a newly created skill."
    )
    ap.add_argument("--new-skill", required=True, help="New skill folder name.")
    ap.add_argument("--skills-dir", default=".agents/skills", help="Skills root to scan.")
    ap.add_argument("--probe", action="append", default=[], help="Probe term (repeatable).")
    ap.add_argument("--top", type=int, default=12, help="Max candidates to report.")
    ap.add_argument("--json", action="store_true", help="Emit JSON (default is JSON).")
    args = ap.parse_args()

    root = pathlib.Path(args.skills_dir)
    if not root.is_dir():
        sys.stderr.write("error: skills dir not found: %s\n" % root)
        return 2

    new_md = root / args.new_skill / "SKILL.md"
    if not new_md.is_file():
        matches = [p for p in root.rglob(args.new_skill + "/SKILL.md")]
        if not matches:
            sys.stderr.write("error: SKILL.md not found for: %s\n" % args.new_skill)
            return 3
        new_md = matches[0]

    probes = [p.lower() for p in args.probe] or derive_probes(new_md)
    if not probes:
        sys.stderr.write("error: no probe terms derivable; pass --probe\n")
        return 2

    scores = collections.Counter()
    evidence = collections.defaultdict(list)
    reverse = []

    for skill_md in sorted(root.rglob("SKILL.md")):
        skill = skill_md.parent.name
        if skill_md == new_md:
            continue
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        low = text.lower()
        if args.new_skill in low:
            reverse.append(skill)
        hits = 0
        for term in probes:
            if term in low:
                hits += 1
                if len(evidence[skill]) < 3:
                    for n, line in enumerate(low.splitlines(), start=1):
                        if term in line:
                            evidence[skill].append({"term": term, "line": n})
                            break
        if hits:
            scores[skill] = hits

    candidates = [
        {
            "skill": skill,
            "matched_probes": scores[skill],
            "evidence": evidence[skill],
        }
        for skill, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[: args.top]
    ]

    payload = {
        "new_skill": args.new_skill,
        "probe_terms": probes,
        "reverse_links": sorted(reverse),
        "reverse_link_count": len(reverse),
        "candidates": candidates,
        "next_step": (
            "For each candidate, decide ADD or DECLINE-with-reason, then run "
            "skill-cross-reference-audit AFTER the edits."
        ),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())