#!/usr/bin/env python3
"""
audit-symlinks.py
=================

Walks a directory for symlinks pointing at any path containing a configurable
private-repo marker (default: ``configurations-private``) and reports per link:
target absolute path, target-exists?, case-matches?, consumer hit count.

Usage
-----
    python3 audit-symlinks.py [--marker configurations-private] [--root .]

Exit codes
----------
0  every link resolves AND every linked file has >=1 consumer
1  at least one link is broken OR at least one linked file has zero consumers
2  bad arguments

Tier
----
Tier-1 (Python) per ``scripting-language-selection-rules.md`` — filesystem
walking, symlink + case-sensitivity comparison, recursive content search.
Ported from ``audit-symlinks.bash`` per ``script-language-tier-port``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

CONSUMER_SUFFIXES = {".kt", ".java", ".dart", ".js", ".ts", ".py"}


def find_symlinks(root: Path, marker: str) -> list[Path]:
    matches: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for name in dirnames + filenames:
            full = Path(dirpath) / name
            if not full.is_symlink():
                continue
            try:
                target = os.readlink(full)
            except OSError:
                continue
            if marker in target:
                matches.append(full)
    return matches


def count_consumers(root: Path, needle: str) -> int:
    count = 0
    for dirpath, _dirs, files in os.walk(root, followlinks=False):
        for fname in files:
            if Path(fname).suffix not in CONSUMER_SUFFIXES:
                continue
            full = Path(dirpath) / fname
            try:
                if needle in full.read_text(errors="ignore"):
                    count += 1
            except OSError:
                continue
    return count


def case_status(link: Path, raw_target: str, resolved: Path | None, exists: bool) -> str:
    if not exists:
        return "N/A"
    if not raw_target.startswith("/"):
        return "relative (skipped)"
    assert resolved is not None
    try:
        real_dir = resolved.parent.resolve(strict=True)
    except OSError:
        return "N/A"
    real = str(real_dir / resolved.name)
    if real == raw_target:
        return "OK"
    return f"MISMATCH (target: {raw_target}, real: {real})"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Audit symlinks pointing at a marker path.")
    ap.add_argument("--marker", default="configurations-private")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)

    root = Path(args.root)
    print(f"Auditing symlinks under {args.root} containing marker '{args.marker}'...")
    print()

    links = find_symlinks(root, args.marker)
    if not links:
        print("No symlinks containing marker found.")
        return 0

    exit_code = 0
    for link in links:
        try:
            raw_target = os.readlink(link)
        except OSError:
            raw_target = ""

        resolved: Path | None
        try:
            resolved = link.resolve(strict=False)
        except OSError:
            resolved = None

        exists = bool(resolved and resolved.exists())
        exists_label = "YES" if exists else "NO"

        cs = case_status(link, raw_target, resolved, exists)
        consumers = count_consumers(root, link.name)

        print(f"Link:       {link}")
        print(f"  Target:   {raw_target}")
        print(f"  Resolved: {resolved if resolved else '<unresolved>'}")
        print(f"  Exists:   {exists_label}")
        print(f"  Case:     {cs}")
        print(f"  Consumers: {consumers}")
        print()

        if not exists:
            exit_code = 1
        if consumers == 0:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
