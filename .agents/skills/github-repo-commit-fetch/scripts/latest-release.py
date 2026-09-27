#!/usr/bin/env python3
"""latest-release.py — Get the latest GitHub release tag for a repo via `gh api`.

Emits a minimal JSON object {tag_name, name, published_at} for the most
recent published release (not prerelease / draft) on the default branch.
Useful as the "backend-native truth" probe when checking whether a tool
pinned via a mise `github:` backend is current (see `mise-tool-management`
Layer 2 §2.2.2).

Exit codes
----------
    0  ok
    1  gh missing / API error / no published release
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
    p = argparse.ArgumentParser(description="Fetch latest release tag via gh api.")
    p.add_argument("--repo", required=True, help="owner/name")
    args = p.parse_args()

    if shutil.which("gh") is None:
        die("gh CLI not found. See `github-rest-api-fallback`.", 1)

    endpoint = f"repos/{args.repo}/releases/latest"
    cp = subprocess.run(
        ["gh", "api", endpoint],
        capture_output=True, text=True, encoding="utf-8",
    )
    if cp.returncode != 0:
        die(f"gh api {endpoint} failed (no published release?): {cp.stderr.strip()}", 1)

    try:
        raw = json.loads(cp.stdout)
    except json.JSONDecodeError as e:
        die(f"non-JSON response: {e}", 1)

    if not raw.get("tag_name"):
        die(f"release has no tag_name: {raw.get('name')}", 1)

    json.dump(
        {
            "tag_name": raw["tag_name"],
            "name": raw.get("name"),
            "published_at": raw.get("published_at"),
        },
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())