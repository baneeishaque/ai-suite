#!/usr/bin/env python3
"""check-name-conflicts.py — check whether repo names are free under an owner.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib; no pip dependencies.

For each candidate name, performs an authenticated lookup of
`GET /repos/<owner>/<name>` and classifies the response:

    200 -> TAKEN      (a repo with this name exists under <owner>)
    404 -> AVAILABLE  (no such repo is visible to the supplied token)
    other / unparseable -> UNKNOWN

The lookup runs with the OWNER's token (`--token-user`), so private repos are
visible and cannot be misreported as AVAILABLE. `--enumerate` additionally
paginates `GET /user/repos` (affiliation=owner, includes private) and reports
the owner's total repo count — exposing the blindness of public-only listing
shortcuts such as `--limit`.

Usage:
    python3 check-name-conflicts.py --owner <login> --repos a,b,c
    python3 check-name-conflicts.py --owner <login> --repos-file names.txt --enumerate

Exit codes:
    0  all candidate names AVAILABLE
    1  at least one TAKEN or UNKNOWN
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

NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
STATUS_LINE_RE = re.compile(r"^HTTP/\S+\s+(\d{3})")
STDERR_STATUS_RE = re.compile(r"\(HTTP (\d{3})\)")
NAME_MAX = 100


def die(msg: str, code: int = 2) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def gh(args: list[str], token: str | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
    try:
        return subprocess.run(
            ["gh", *args], capture_output=True, text=True, encoding="utf-8",
            env=env, timeout=60,
        )
    except OSError as exc:
        die(f"cannot run gh: {exc}")
    except subprocess.TimeoutExpired:
        die("gh call timed out after 60s")


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


def parse_status(proc: subprocess.CompletedProcess) -> int | None:
    for line in proc.stdout.splitlines():
        match = STATUS_LINE_RE.match(line)
        if match:
            return int(match.group(1))
    match = STDERR_STATUS_RE.search(proc.stderr)
    return int(match.group(1)) if match else None


def lookup(owner: str, name: str, token: str | None) -> tuple[str, int | None]:
    proc = gh(["api", "--include", f"repos/{owner}/{name}"], token)
    code = parse_status(proc)
    if code == 200:
        return "TAKEN", code
    if code == 404:
        return "AVAILABLE", code
    return "UNKNOWN", code


def enumerate_owner_repos(token: str | None) -> list[str]:
    names: list[str] = []
    page = 1
    while True:
        proc = gh(["api", f"user/repos?per_page=100&affiliation=owner&page={page}",
                   "--jq", ".[].name"], token)
        if proc.returncode != 0:
            die(f"enumeration failed on page {page}: {proc.stderr.strip()}")
        batch = [line for line in proc.stdout.splitlines() if line.strip()]
        names.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return names


def load_candidates(args: argparse.Namespace) -> list[str]:
    names: list[str] = []
    if args.repos:
        names.extend(part.strip() for part in args.repos.split(","))
    if args.repos_file:
        try:
            with open(args.repos_file, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        names.append(line)
        except OSError as exc:
            die(f"cannot read --repos-file: {exc}")
    seen: set[str] = set()
    unique: list[str] = []
    for name in names:
        if name and name not in seen:
            seen.add(name)
            unique.append(name)
    if not unique:
        die("no candidate names (use --repos and/or --repos-file)")
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description="Repo-name conflict check.")
    parser.add_argument("--owner", required=True,
                        help="owner login to check names under")
    parser.add_argument("--repos", help="comma-separated candidate repo names")
    parser.add_argument("--repos-file",
                        help="file with one candidate name per line")
    parser.add_argument("--token-user",
                        help="gh-authenticated login whose token to use")
    parser.add_argument("--enumerate", action="store_true",
                        help="also paginate the owner's full repo list (includes private)")
    args = parser.parse_args()

    token = resolve_token(args.token_user) if args.token_user else None
    candidates = load_candidates(args)

    enum_set: set[str] | None = None
    if args.enumerate:
        enum_names = enumerate_owner_repos(token)
        enum_set = set(enum_names)
        print(json.dumps({"enumerated_total": len(enum_names)}), flush=True)

    counts = {"TAKEN": 0, "AVAILABLE": 0, "UNKNOWN": 0}
    taken: list[str] = []
    available: list[str] = []
    unknown: list[str] = []

    for name in candidates:
        if not NAME_RE.match(name) or len(name) > NAME_MAX:
            status, http_status, reason = "UNKNOWN", None, "invalid repo name"
        else:
            status, http_status = lookup(args.owner, name, token)
            reason = "" if status != "UNKNOWN" else "unexpected API response"

        record = {"repo": name, "owner": args.owner, "status": status,
                  "http_status": http_status}
        if reason:
            record["reason"] = reason
        if enum_set is not None:
            record["in_enumeration"] = name in enum_set
        print(json.dumps(record), flush=True)

        counts[status] += 1
        if status == "TAKEN":
            taken.append(name)
        elif status == "AVAILABLE":
            available.append(name)
        else:
            unknown.append(name)

    print(json.dumps({
        "owner": args.owner,
        "checked": len(candidates),
        "taken": taken,
        "available": available,
        "unknown": unknown,
        "counts": counts,
    }), flush=True)

    return 0 if counts["TAKEN"] == 0 and counts["UNKNOWN"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
