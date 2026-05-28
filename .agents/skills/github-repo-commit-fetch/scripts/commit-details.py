#!/usr/bin/env python3
"""commit-details.py — Get a single commit's details (message, files, author, date) via `gh api`.

Emits a JSON document with sha, author, date, message, and the list of
changed files (filename + status + additions/deletions) for one commit.

Exit codes
----------
    0  ok
    1  gh missing / API error / commit not found
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
    p = argparse.ArgumentParser(description="Fetch one commit's details via gh api.")
    p.add_argument("--repo", required=True, help="owner/name")
    p.add_argument("--sha", required=True, help="full or short commit SHA (or branch/tag)")
    p.add_argument("--files-only", action="store_true", help="print only the filename list")
    args = p.parse_args()

    if shutil.which("gh") is None:
        die("gh CLI not found. See `github-rest-api-fallback`.", 1)

    endpoint = f"repos/{args.repo}/commits/{args.sha}"
    cp = subprocess.run(
        ["gh", "api", endpoint],
        capture_output=True, text=True, encoding="utf-8",
    )
    if cp.returncode != 0:
        die(f"gh api {endpoint} failed: {cp.stderr.strip()}", 1)

    try:
        raw = json.loads(cp.stdout)
    except json.JSONDecodeError as e:
        die(f"non-JSON response: {e}", 1)

    if args.files_only:
        for f in raw.get("files", []):
            print(f["filename"])
        return 0

    projected = {
        "sha": raw["sha"],
        "short": raw["sha"][:8],
        "author": raw["commit"]["author"]["name"],
        "author_email": raw["commit"]["author"]["email"],
        "date": raw["commit"]["author"]["date"],
        "message": raw["commit"]["message"],
        "files": [
            {
                "filename": f["filename"],
                "status": f.get("status"),
                "additions": f.get("additions"),
                "deletions": f.get("deletions"),
            }
            for f in raw.get("files", [])
        ],
    }
    json.dump(projected, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
