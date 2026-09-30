#!/usr/bin/env python3
"""check-destination-conflicts.py — pre-transfer gate: destination conflicts.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib; no pip dependencies.

Composite over github-repo-name-conflict-check: shells out to its
`check-name-conflicts.py` with the destination owner and the transfer repo
list, streams the per-name verdicts, and emits a transfer gate summary. The
gate passes only when every candidate name is AVAILABLE.

Usage:
    python3 check-destination-conflicts.py --destination-owner <login> \
        --repos a,b [--token-user <login>] [--enumerate]

Exit codes:
    0  gate pass (all names AVAILABLE)
    1  gate block (any TAKEN or UNKNOWN)
    2  usage / configuration error
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import NoReturn


def die(msg: str, code: int = 2) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def skills_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "skill-factory" / "SKILL.md").is_file():
            return parent
    die("cannot locate .agents/skills root (skill-factory marker missing)")


def base_script() -> Path:
    base = (skills_root() / "github" / "repo" / "github-repo-name-conflict-check"
            / "scripts" / "check-name-conflicts.py")
    if not base.is_file():
        die(f"base skill script not found: {base}")
    return base


def main() -> int:
    parser = argparse.ArgumentParser(description="Transfer destination gate.")
    parser.add_argument("--destination-owner", required=True,
                        help="account receiving the transfers")
    parser.add_argument("--repos", help="comma-separated transfer repo names")
    parser.add_argument("--repos-file",
                        help="file with one repo name per line")
    parser.add_argument("--token-user",
                        help="gh-authenticated login whose token to use")
    parser.add_argument("--enumerate", action="store_true",
                        help="also report the destination's repo count")
    args = parser.parse_args()

    if not args.repos and not args.repos_file:
        die("no repos (use --repos and/or --repos-file)")

    base_args = [sys.executable, str(base_script()),
                 "--owner", args.destination_owner]
    if args.repos:
        base_args += ["--repos", args.repos]
    if args.repos_file:
        base_args += ["--repos-file", args.repos_file]
    if args.token_user:
        base_args += ["--token-user", args.token_user]
    if args.enumerate:
        base_args.append("--enumerate")

    proc = subprocess.run(base_args)
    if proc.returncode not in (0, 1):
        return 2

    gate = "pass" if proc.returncode == 0 else "block"
    print(json.dumps({"gate": gate,
                      "destination_owner": args.destination_owner}), flush=True)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
