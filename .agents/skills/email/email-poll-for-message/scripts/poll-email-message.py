#!/usr/bin/env python3
"""poll-email-message.py — poll a mailbox until a matching email arrives.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib; no pip dependencies.

Composite over the poll-until base primitive: shells out to `poll-until.py`
(never re-implements the polling loop) with this skill's `search-messages.py`
as the check command. The password is read from the environment by the search
script; it is never passed as a command-line argument.

Usage:
    python3 poll-email-message.py --imap-host <host> --username <user> \
        [--subject-contains <text>] [--interval 30] [--attempts 20]

Exit codes:
    0  matching message arrived
    1  attempts exhausted
    2  usage / configuration error
"""
from __future__ import annotations

import argparse
import json
import os
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
    base = (skills_root() / "general" / "polling" / "poll-until"
            / "scripts" / "poll-until.py")
    if not base.is_file():
        die(f"base skill script not found: {base}")
    return base


def search_script() -> Path:
    sibling = Path(__file__).resolve().parent / "search-messages.py"
    if not sibling.is_file():
        die(f"search script not found: {sibling}")
    return sibling


def build_check(args: argparse.Namespace) -> list[str]:
    check = [sys.executable, str(search_script()),
             "--password-env", args.password_env,
             "--mailbox", args.mailbox,
             "--limit", str(args.limit)]
    if args.source_file:
        check += ["--source-file", args.source_file]
    else:
        check += ["--imap-host", args.imap_host,
                  "--imap-port", str(args.imap_port),
                  "--username", args.username]
    if not args.ssl:
        check.append("--no-ssl")
    if args.subject_contains:
        check += ["--subject-contains", args.subject_contains]
    if args.from_contains:
        check += ["--from-contains", args.from_contains]
    if args.unseen:
        check.append("--unseen")
    if args.since_days:
        check += ["--since-days", str(args.since_days)]
    return check


def main() -> int:
    parser = argparse.ArgumentParser(description="Mailbox poller.")
    parser.add_argument("--imap-host", help="IMAP host (or use --source-file)")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--username", help="mailbox login (or use --source-file)")
    parser.add_argument("--password-env", default="EMAIL_PASSWORD",
                        help="environment variable holding the password")
    parser.add_argument("--mailbox", default="INBOX")
    parser.add_argument("--subject-contains")
    parser.add_argument("--from-contains")
    parser.add_argument("--unseen", action="store_true")
    parser.add_argument("--since-days", type=int)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--interval", type=float, default=30.0,
                        help="seconds between attempts (default 30)")
    parser.add_argument("--attempts", type=int, default=20,
                        help="maximum attempts (default 20)")
    parser.add_argument("--source-file",
                        help="offline JSONL fixture instead of IMAP")
    parser.add_argument("--ssl", action=argparse.BooleanOptionalAction,
                        default=True, help="use IMAP over SSL (default)")
    args = parser.parse_args()

    if not args.source_file:
        if not args.imap_host or not args.username:
            die("--imap-host and --username are required (or use --source-file)")
        if not os.environ.get(args.password_env):
            die(f"password env var {args.password_env!r} is not set")

    check = build_check(args)
    poll = [sys.executable, str(base_script()),
            "--interval", str(args.interval),
            "--attempts", str(args.attempts),
            "--label", "email", "--", *check]
    proc = subprocess.run(poll)

    verdict = "arrived" if proc.returncode == 0 else "exhausted"
    print(json.dumps({"verdict": verdict, "label": "email"}), flush=True)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
