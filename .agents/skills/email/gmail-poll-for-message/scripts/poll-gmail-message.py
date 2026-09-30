#!/usr/bin/env python3
"""poll-gmail-message.py — Gmail preset: poll a Gmail mailbox until a match.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib; no pip dependencies.

Composite (preset) over email-poll-for-message: shells out to its
`poll-email-message.py` driver with the Gmail IMAP endpoint and the Gmail
credential convention fixed. Never re-implements polling or IMAP logic.

Prerequisite: IMAP enabled in Gmail and an app password created. The app
password is read from the environment variable named by --password-env
(default GMAIL_APP_PASSWORD).

Usage:
    python3 poll-gmail-message.py --username <gmail-address> \
        [--subject-contains <text>] [--interval 30] [--attempts 20]

Exit codes:
    0  matching message arrived
    1  attempts exhausted
    2  usage / configuration error
"""
from __future__ import annotations

import argparse
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


def base_driver() -> Path:
    driver = (skills_root() / "email" / "email-poll-for-message"
              / "scripts" / "poll-email-message.py")
    if not driver.is_file():
        die(f"base skill script not found: {driver}")
    return driver


def main() -> int:
    parser = argparse.ArgumentParser(description="Gmail mailbox poller preset.")
    parser.add_argument("--username", help="Gmail address (or use --source-file)")
    parser.add_argument("--password-env", default="GMAIL_APP_PASSWORD",
                        help="environment variable holding the app password")
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
    args = parser.parse_args()

    if not args.source_file and not args.username:
        die("--username is required (or use --source-file)")

    driver_args = [sys.executable, str(base_driver()),
                   "--imap-host", "imap.gmail.com",
                   "--imap-port", "993",
                   "--password-env", args.password_env,
                   "--mailbox", args.mailbox,
                   "--limit", str(args.limit),
                   "--interval", str(args.interval),
                   "--attempts", str(args.attempts)]
    if args.username:
        driver_args += ["--username", args.username]
    if args.source_file:
        driver_args += ["--source-file", args.source_file]
    if args.subject_contains:
        driver_args += ["--subject-contains", args.subject_contains]
    if args.from_contains:
        driver_args += ["--from-contains", args.from_contains]
    if args.unseen:
        driver_args.append("--unseen")
    if args.since_days:
        driver_args += ["--since-days", str(args.since_days)]

    proc = subprocess.run(driver_args)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
