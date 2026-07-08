#!/usr/bin/env python3
"""list-commits.py — List recent commits on a repo via `gh api`.

Emits a JSON array of {sha, date, author, message} for the N most recent
commits on the default (or specified) branch. Pure-stdlib Python wrapper
over `gh api repos/<repo>/commits` with a jq projection.

Exit codes
----------
    0  ok
    1  gh missing / API error
    2  config error
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def main() -> int:
    p = argparse.ArgumentParser(description="List recent commits via gh api.")
    p.add_argument("--repo", required=True, help="owner/name")
    p.add_argument("--limit", type=int, default=10, help="how many commits (default 10)")
    p.add_argument("--branch", help="branch / ref to list from (default: repo default)")
    p.add_argument("--path", help="restrict to commits touching this path")
    args = p.parse_args()

    if shutil.which("gh") is None:
        die("gh CLI not found. See `github-rest-api-fallback`.", 1)

    endpoint = f"repos/{args.repo}/commits?per_page={args.limit}"
    if args.branch:
        endpoint += f"&sha={args.branch}"
    if args.path:
        endpoint += f"&path={args.path}"

    jq = (
        f".[0:{args.limit}] | map({{sha: .sha, short: .sha[0:8], "
        'date: .commit.author.date, author: .commit.author.name, '
        'message: (.commit.message | split("\\n")[0])})'
    )
    cp = subprocess.run(
        ["gh", "api", endpoint, "--jq", jq],
        capture_output=True, text=True, encoding="utf-8",
    )
    if cp.returncode != 0:
        die(f"gh api failed: {cp.stderr.strip()}", 1)

    out = cp.stdout.strip()
    try:
        data = json.loads(out) if out else []
    except json.JSONDecodeError:
        data = [json.loads(line) for line in out.splitlines() if line.strip()]
    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
