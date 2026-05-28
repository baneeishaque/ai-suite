#!/usr/bin/env python3
"""fetch-file-at-ref.py — Download a single repo file at a specific ref via `gh api`.

Resolves the contents API's `download_url` for `<path>` at `<ref>` and
streams the body to `<out>`. Uses urllib (no curl, no shell quoting hazards).

Exit codes
----------
    0  file fetched successfully
    1  gh CLI missing / API error / download failed
    2  configuration error
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def ensure_gh() -> None:
    if shutil.which("gh") is None:
        die("gh CLI not found. See sibling skill `github-rest-api-fallback`.", 1)


def gh_api_json(endpoint: str, jq: str | None = None) -> object:
    args = ["gh", "api", endpoint]
    if jq:
        args += ["--jq", jq]
    cp = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    if cp.returncode != 0:
        die(f"gh api {endpoint} failed: {cp.stderr.strip()}")
    out = cp.stdout.strip()
    if jq:
        # --jq strips JSON quoting for string results
        return out
    return json.loads(out) if out else None


def main() -> int:
    p = argparse.ArgumentParser(description="Fetch a repo file at a specific ref.")
    p.add_argument("--repo", required=True, help="owner/name")
    p.add_argument("--ref", required=True, help="sha, branch, or tag")
    p.add_argument("--path", required=True, help="path inside the repo")
    p.add_argument("--out", required=True, help="local destination path")
    args = p.parse_args()

    ensure_gh()

    endpoint = f"repos/{args.repo}/contents/{args.path}?ref={args.ref}"
    url = gh_api_json(endpoint, jq=".download_url")
    if not url or url == "null":
        die(f"no download_url for {args.path}@{args.ref}", 1)
    if not isinstance(url, str):
        die(f"unexpected download_url type: {type(url).__name__}", 1)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url) as resp, out.open("wb") as fh:
            shutil.copyfileobj(resp, fh)
    except Exception as e:  # noqa: BLE001
        die(f"download failed: {e}", 1)

    size = out.stat().st_size
    print(f"OK: {out} ({size:,} bytes) from {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
