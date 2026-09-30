#!/usr/bin/env python3
"""initiate-repo-transfers.py — initiate GitHub repository transfers.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib; drives the `gh api` CLI.

For each repository, calls `POST /repos/<old-owner>/<repo>/transfer` with
`new_owner=<destination-owner>`. The endpoint returns 202 Accepted; the actual
transfer completes only after the destination account accepts the confirmation
EMAIL (acceptance is email-based; the collaborator-invitation API path is not
applicable to transfers; unaccepted invitations expire after 1 day).

Safety: DRY-RUN by default — nothing is sent without --execute.

Usage:
    python3 initiate-repo-transfers.py --old-owner <login> \
        --destination-owner <login> --repos a,b [--token-user <login>] [--execute]

Exit codes:
    0  all transfers accepted (or all planned in dry-run)
    1  at least one initiation failed
    2  usage / configuration error
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import NoReturn

STDERR_STATUS_RE = re.compile(r"\(HTTP (\d{3})\)")
STATUS_LINE_RE = re.compile(r"^HTTP/\S+\s+(\d{3})")


def die(msg: str, code: int = 2) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


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


def parse_status(stdout: str, stderr: str) -> int | None:
    for line in stdout.splitlines():
        match = STATUS_LINE_RE.match(line)
        if match:
            return int(match.group(1))
    match = STDERR_STATUS_RE.search(stderr)
    return int(match.group(1)) if match else None


def load_repos(args: argparse.Namespace) -> list[str]:
    repos: list[str] = []
    if args.repos:
        repos.extend(part.strip() for part in args.repos.split(","))
    if args.repos_file:
        try:
            with open(args.repos_file, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        repos.append(line)
        except OSError as exc:
            die(f"cannot read --repos-file: {exc}")
    seen: set[str] = set()
    unique: list[str] = []
    for repo in repos:
        if repo and repo not in seen:
            seen.add(repo)
            unique.append(repo)
    if not unique:
        die("no repos (use --repos and/or --repos-file)")
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description="Initiate repo transfers.")
    parser.add_argument("--old-owner", required=True, help="current owner")
    parser.add_argument("--destination-owner", required=True,
                        help="receiving account")
    parser.add_argument("--repos", help="comma-separated repo names")
    parser.add_argument("--repos-file", help="file with one repo name per line")
    parser.add_argument("--token-user",
                        help="gh-authenticated login whose token to use")
    parser.add_argument("--execute", action="store_true",
                        help="actually send the POST requests (default: dry-run)")
    args = parser.parse_args()

    repos = load_repos(args)

    env = os.environ.copy()
    if args.token_user:
        env["GH_TOKEN"] = resolve_token(args.token_user)

    failed: list[str] = []
    for repo in repos:
        endpoint = f"repos/{args.old_owner}/{repo}/transfer"
        if not args.execute:
            print(json.dumps({
                "repo": repo, "dry_run": True, "method": "POST",
                "endpoint": endpoint, "new_owner": args.destination_owner,
            }), flush=True)
            continue

        try:
            proc = subprocess.run(
                ["gh", "api", "--include", "-X", "POST", endpoint,
                 "-f", f"new_owner={args.destination_owner}"],
                capture_output=True, text=True, encoding="utf-8",
                env=env, timeout=60,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            die(f"cannot run gh: {exc}")

        status = parse_status(proc.stdout, proc.stderr)
        accepted = status == 202
        record = {"repo": repo, "http_status": status, "accepted": accepted}
        if not accepted:
            record["detail"] = proc.stderr.strip()[:200]
            failed.append(repo)
        print(json.dumps(record), flush=True)

    if args.execute and not failed:
        print(json.dumps({"note": (
            "acceptance is email-based — the destination user must accept the "
            "confirmation email; unaccepted invitations expire after 1 day"
        )}), flush=True)

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
