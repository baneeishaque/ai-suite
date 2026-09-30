#!/usr/bin/env python3
"""poll-transfer-completion.py — wait until transferred repos land under the new owner.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib; no pip dependencies.

Composite over github-api-poll-until: shells out to its `poll-api-until.py`
with the transfer-landing endpoint under the destination owner
(`repos/<destination>/{item}`, expect 200), streams the base output, and emits
a transfer-scoped landed/pending summary parsed from the base's final summary
line.

Usage:
    python3 poll-transfer-completion.py --destination-owner <login> \
        --repos a,b [--interval 15] [--attempts 20] [--token-user <login>]

Exit codes:
    0  every repository landed
    1  at least one repository still pending
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
    base = (skills_root() / "github" / "github-api-poll-until"
            / "scripts" / "poll-api-until.py")
    if not base.is_file():
        die(f"base skill script not found: {base}")
    return base


def parse_summary(stdout: str) -> dict | None:
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "met" in data and "unmet" in data:
            return data
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Transfer completion stage.")
    parser.add_argument("--destination-owner", required=True,
                        help="account receiving the repositories")
    parser.add_argument("--repos", help="comma-separated repo names")
    parser.add_argument("--repos-file", help="file with one repo name per line")
    parser.add_argument("--interval", type=float, default=15.0,
                        help="seconds between attempts (default 15)")
    parser.add_argument("--attempts", type=int, default=20,
                        help="maximum attempts (default 20)")
    parser.add_argument("--token-user",
                        help="gh-authenticated login whose token to use")
    args = parser.parse_args()

    if not args.repos and not args.repos_file:
        die("no repos (use --repos and/or --repos-file)")

    endpoint = f"repos/{args.destination_owner}/{{item}}"
    base_args = [sys.executable, str(base_script()),
                 "--endpoint", endpoint, "--expect", "200",
                 "--interval", str(args.interval),
                 "--attempts", str(args.attempts)]
    if args.repos:
        base_args += ["--items", args.repos]
    if args.repos_file:
        base_args += ["--items-file", args.repos_file]
    if args.token_user:
        base_args += ["--token-user", args.token_user]

    proc = subprocess.run(base_args, capture_output=True, text=True,
                          encoding="utf-8")
    sys.stdout.write(proc.stdout or "")
    sys.stdout.flush()
    if proc.returncode not in (0, 1):
        return 2

    summary = parse_summary(proc.stdout or "")
    if summary is None:
        die("cannot parse the base poller summary")

    print(json.dumps({"landed": summary.get("met", []),
                      "pending": summary.get("unmet", [])}), flush=True)
    return 0 if not summary.get("unmet") else 1


if __name__ == "__main__":
    sys.exit(main())
