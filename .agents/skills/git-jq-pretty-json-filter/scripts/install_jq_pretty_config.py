#!/usr/bin/env python3
"""
install_jq_pretty_config.py — idempotently install the jq-pretty Git filter.

Inserts the [filter "jq-pretty"] and [diff "jq-pretty"] blocks into a target
Git config file (default: $HOME/.gitconfig). Already-present keys are not
re-written.

Block written:
    [filter "jq-pretty"]
        clean = jq --indent 4 .
        smudge = cat
        required = true
    [diff "jq-pretty"]
        textconv = jq --indent 4 .
        cachetextconv = true

Usage:
    install_jq_pretty_config.py [--target PATH] [--dry-run]

Exit codes:
    0  success (or dry-run)
    1  git config command failed
    2  jq binary missing
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

KEYS: list[tuple[str, str]] = [
    ("filter.jq-pretty.clean",      "jq --indent 4 ."),
    ("filter.jq-pretty.smudge",     "cat"),
    ("filter.jq-pretty.required",   "true"),
    ("diff.jq-pretty.textconv",     "jq --indent 4 ."),
    ("diff.jq-pretty.cachetextconv", "true"),
]


def get_key(target: Path, key: str) -> str | None:
    res = subprocess.run(
        ["git", "config", "--file", str(target), "--get", key],
        text=True, encoding="utf-8", capture_output=True,
    )
    if res.returncode == 0:
        return res.stdout.rstrip("\n")
    return None


def set_key(target: Path, key: str, value: str) -> None:
    subprocess.run(
        ["git", "config", "--file", str(target), key, value],
        check=True, text=True, encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", type=Path,
                    default=Path(os.environ.get("HOME", "")) / ".gitconfig")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not shutil.which("jq"):
        print("ERROR: 'jq' not found on PATH. Install jq before using this filter.",
              file=sys.stderr)
        return 2

    target: Path = args.target
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.touch()

    added = 0
    kept = 0
    for key, want in KEYS:
        have = get_key(target, key)
        if have == want:
            kept += 1
            print(f"  ok    {key} = {want}")
            continue
        if args.dry_run:
            print(f"  [dry] would set {key} = {want}"
                  + (f"  (was: {have})" if have is not None else ""))
            added += 1
            continue
        try:
            set_key(target, key, want)
        except subprocess.CalledProcessError as e:
            print(f"ERROR: git config failed for {key}: {e}", file=sys.stderr)
            return 1
        added += 1
        print(f"  set   {key} = {want}")

    print(f"target: {target}")
    print(f"kept: {kept}   {'would-add' if args.dry_run else 'added'}: {added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
