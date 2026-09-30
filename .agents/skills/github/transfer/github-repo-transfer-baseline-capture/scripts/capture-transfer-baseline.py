#!/usr/bin/env python3
"""capture-transfer-baseline.py — capture pre-transfer state under the old owner.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib; no pip dependencies.

Composite over github-repo-state-fingerprint: shells out to its `capture`
subcommand with the old owner and the transfer repo list, then reads the
written snapshot and emits a transfer-scoped summary (snapshot path + per-repo
head SHAs) for later verification stages.

Usage:
    python3 capture-transfer-baseline.py --old-owner <login> --repos a,b \
        --output baseline.json [--token-user <login>]

Exit codes:
    0  all repositories captured
    1  any repository missing or errored
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
    base = (skills_root() / "github" / "repo" / "github-repo-state-fingerprint"
            / "scripts" / "repo-state-fingerprint.py")
    if not base.is_file():
        die(f"base skill script not found: {base}")
    return base


def main() -> int:
    parser = argparse.ArgumentParser(description="Transfer baseline stage.")
    parser.add_argument("--old-owner", required=True,
                        help="current owner of the repositories")
    parser.add_argument("--repos", help="comma-separated repo names")
    parser.add_argument("--repos-file", help="file with one repo name per line")
    parser.add_argument("--output", required=True, help="snapshot file to write")
    parser.add_argument("--token-user",
                        help="gh-authenticated login whose token to use")
    args = parser.parse_args()

    if not args.repos and not args.repos_file:
        die("no repos (use --repos and/or --repos-file)")

    base_args = [sys.executable, str(base_script()), "capture",
                 "--owner", args.old_owner,
                 "--output", args.output]
    if args.repos:
        base_args += ["--repos", args.repos]
    if args.repos_file:
        base_args += ["--repos-file", args.repos_file]
    if args.token_user:
        base_args += ["--token-user", args.token_user]

    proc = subprocess.run(base_args)
    if proc.returncode not in (0, 1):
        return 2

    try:
        with open(args.output, encoding="utf-8") as fh:
            snapshot = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        die(f"cannot read written snapshot {args.output}: {exc}")

    repos = snapshot.get("repos", {})
    head_shas = {name: record.get("head_sha", "")
                 for name, record in repos.items()
                 if record.get("status") == "captured"}
    print(json.dumps({
        "snapshot": args.output,
        "old_owner": args.old_owner,
        "captured": len(head_shas),
        "head_shas": head_shas,
    }), flush=True)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
