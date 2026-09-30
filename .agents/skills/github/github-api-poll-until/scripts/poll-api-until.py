#!/usr/bin/env python3
"""poll-api-until.py — poll GitHub API endpoints per item until expected status.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib; no pip dependencies.

Composite over the poll-until base primitive: shells out to `poll-until.py`
(never re-implements the polling loop) and supplies a `gh api` status check per
item through its internal `_check` subcommand. `{item}` in the endpoint
template is replaced per item.

Usage:
    python3 poll-api-until.py --endpoint "repos/<owner>/{item}" --items a,b \
        [--expect 200] [--interval 10] [--attempts 12] [--token-user <login>]

Exit codes:
    0  every item reached the expected status
    1  at least one item exhausted its attempts
    2  usage / configuration error
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

STDERR_STATUS_RE = re.compile(r"\(HTTP (\d{3})\)")
STATUS_LINE_RE = re.compile(r"^HTTP/\S+\s+(\d{3})")


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


def check_status(endpoint: str) -> int | None:
    try:
        proc = subprocess.run(
            ["gh", "api", "--include", endpoint],
            capture_output=True, text=True, encoding="utf-8", timeout=60,
        )
    except OSError as exc:
        die(f"cannot run gh: {exc}")
    except subprocess.TimeoutExpired:
        return None
    for line in proc.stdout.splitlines():
        match = STATUS_LINE_RE.match(line)
        if match:
            return int(match.group(1))
    match = STDERR_STATUS_RE.search(proc.stderr)
    return int(match.group(1)) if match else None


def run_check(args: argparse.Namespace) -> int:
    status = check_status(args.endpoint)
    print(json.dumps({"endpoint": args.endpoint, "http_status": status}), flush=True)
    return 0 if status == args.expect else 1


def resolve_token(login: str) -> str:
    try:
        proc = subprocess.run(
            ["gh", "auth", "token", "--user", login],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        die(f"cannot resolve token for {login!r}: {exc}")
    token = proc.stdout.strip()
    if proc.returncode != 0 or not token:
        die(f"no stored gh token for user {login!r} (try: gh auth login)")
    return token


def load_items(args: argparse.Namespace) -> list[str]:
    items: list[str] = []
    if args.items:
        items.extend(part.strip() for part in args.items.split(","))
    if args.items_file:
        try:
            with open(args.items_file, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        items.append(line)
        except OSError as exc:
            die(f"cannot read --items-file: {exc}")
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            unique.append(item)
    if not unique:
        die("no items (use --items and/or --items-file)")
    return unique


def main_poll(args: argparse.Namespace) -> int:
    if "{item}" not in args.endpoint:
        die("--endpoint must contain the {item} placeholder")
    items = load_items(args)
    base = base_script()
    self_path = str(Path(__file__).resolve())

    env = os.environ.copy()
    if args.token_user:
        env["GH_TOKEN"] = resolve_token(args.token_user)

    met: list[str] = []
    unmet: list[str] = []
    for item in items:
        endpoint = args.endpoint.replace("{item}", item)
        check = [sys.executable, self_path, "_check",
                 "--endpoint", endpoint, "--expect", str(args.expect)]
        poll = [sys.executable, str(base),
                "--interval", str(args.interval),
                "--attempts", str(args.attempts),
                "--label", item, "--", *check]
        proc = subprocess.run(poll, env=env)
        (met if proc.returncode == 0 else unmet).append(item)

    print(json.dumps({"met": met, "unmet": unmet, "expect": args.expect}), flush=True)
    return 0 if not unmet else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="GitHub API poller.")
    sub = parser.add_subparsers(dest="mode", required=False)

    chk = sub.add_parser("_check", help=argparse.SUPPRESS)
    chk.add_argument("--endpoint", required=True)
    chk.add_argument("--expect", type=int, default=200)

    parser.add_argument("--endpoint", help="endpoint template containing {item}")
    parser.add_argument("--items", help="comma-separated items")
    parser.add_argument("--items-file", help="file with one item per line")
    parser.add_argument("--expect", type=int, default=200,
                        help="expected HTTP status (default 200)")
    parser.add_argument("--interval", type=float, default=10.0,
                        help="seconds between attempts (default 10)")
    parser.add_argument("--attempts", type=int, default=12,
                        help="maximum attempts (default 12)")
    parser.add_argument("--token-user",
                        help="gh-authenticated login whose token to use")

    args = parser.parse_args()
    if args.mode == "_check":
        return run_check(args)
    if not args.endpoint:
        parser.error("--endpoint is required")
    return main_poll(args)


if __name__ == "__main__":
    sys.exit(main())
