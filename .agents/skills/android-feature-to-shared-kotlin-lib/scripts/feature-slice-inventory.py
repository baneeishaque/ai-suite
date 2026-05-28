#!/usr/bin/env python3
"""
feature-slice-inventory.py
==========================

Given a feature name fragment and an Android source root, list the likely
vertical-slice files (Activity / Kotlin / Java source, layout XML,
ApiWrapper / API method references, string resources) that constitute
the feature.

Usage
-----
    python3 feature-slice-inventory.py --feature <name> --root <android-src-root>

Exit codes
----------
0  at least one file matched in at least one section
1  no matches in any section
2  bad arguments

Tier
----
Tier-1 (Python) per ``scripting-language-selection-rules.md`` — string-case
manipulation (PascalCase / snake_case / lowercase) + recursive filesystem
walk + content regex. Ported from ``feature-slice-inventory.bash`` per
``script-language-tier-port``.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

API_MARKER_RE = re.compile(r"ApiWrapper|@POST|@GET|interface Api")


def feature_variants(feature: str) -> tuple[str, str, str]:
    lower = re.sub(r"[ \-_]", "", feature).lower()
    parts = re.split(r"[_ \-]", feature)
    pascal = "".join(p[:1].upper() + p[1:] for p in parts if p)
    snake = re.sub(r"([A-Z])", r"_\1", feature).lower()
    snake = re.sub(r"^_", "", snake)
    snake = re.sub(r"[ \-]", "_", snake)
    return lower, pascal, snake


def iter_files(root: Path):
    for dirpath, _dirs, files in os.walk(root, followlinks=False):
        for f in files:
            yield Path(dirpath) / f


def list_or_none(items: list[str]) -> None:
    if items:
        for item in items:
            print(item)
    else:
        print("(none)")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Inventory a vertical feature slice in an Android source tree.")
    ap.add_argument("--feature", required=True)
    ap.add_argument("--root", required=True)
    args = ap.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"Root not a directory: {root}", file=sys.stderr)
        return 2

    lower, pascal, snake = feature_variants(args.feature)
    print("Feature variants:")
    print(f"  lower:  {lower}")
    print(f"  pascal: {pascal}")
    print(f"  snake:  {snake}")
    print()

    name_re = re.compile("|".join(re.escape(v) for v in (lower, pascal, snake) if v), re.IGNORECASE)
    name_layout_re = re.compile("|".join(re.escape(v) for v in (lower, snake) if v), re.IGNORECASE)

    total_hits = 0

    print("=== Activities & Kotlin/Java source ===")
    sources = sorted(
        str(p) for p in iter_files(root)
        if p.suffix in {".java", ".kt"} and name_re.search(p.name)
    )
    list_or_none(sources)
    total_hits += len(sources)
    print()

    print("=== Layout XML ===")
    layouts = sorted(
        str(p) for p in iter_files(root)
        if p.suffix == ".xml"
        and "/res/layout/" in str(p)
        and name_layout_re.search(p.name)
    )
    list_or_none(layouts)
    total_hits += len(layouts)
    print()

    print("=== ApiWrapper / Api method references ===")
    api_hits: set[str] = set()
    for p in iter_files(root):
        if p.suffix not in {".java", ".kt"}:
            continue
        try:
            body = p.read_text(errors="ignore")
        except OSError:
            continue
        if name_re.search(body) and API_MARKER_RE.search(body):
            api_hits.add(str(p))
    list_or_none(sorted(api_hits))
    total_hits += len(api_hits)
    print()

    print("=== String resources ===")
    strings: list[str] = []
    for p in iter_files(root):
        if p.name != "strings.xml":
            continue
        if "/res/values" not in str(p):
            continue
        try:
            if name_layout_re.search(p.read_text(errors="ignore")):
                strings.append(str(p))
        except OSError:
            continue
    list_or_none(sorted(strings))
    total_hits += len(strings)

    return 0 if total_hits > 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
