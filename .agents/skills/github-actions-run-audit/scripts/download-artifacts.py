#!/usr/bin/env python3
"""download-artifacts.py — Download all artifacts of one workflow run to a directory.

Thin wrapper over `gh run download <run-id> --repo <repo> --dir <dir>`.
Exists so the composer skill's documented invocation is uniform Python
(matching `audit-run.py`) and so the agent can easily compose this with
other audit steps via subprocess.

Exit codes
----------
    0  artifacts downloaded
    1  gh missing / run has no artifacts / API error
    2  config error
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def main() -> int:
    p = argparse.ArgumentParser(description="Download artifacts from one workflow run.")
    p.add_argument("--repo", required=True, help="owner/name")
    p.add_argument("--run-id", required=True, type=int, help="workflow run id")
    p.add_argument("--dir", required=True, help="output directory (created if missing)")
    p.add_argument("--name", action="append", default=[],
                   help="restrict to artifact NAME (repeatable; default: all)")
    args = p.parse_args()

    if shutil.which("gh") is None:
        die("gh CLI not found. See `github-rest-api-fallback`.", 1)

    out_dir = Path(args.dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["gh", "run", "download", str(args.run_id), "--repo", args.repo, "--dir", str(out_dir)]
    for n in args.name:
        cmd += ["--name", n]

    cp = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if cp.returncode != 0:
        die(f"gh run download failed: {cp.stderr.strip()}", 1)

    files = sorted(p.relative_to(out_dir).as_posix() for p in out_dir.rglob("*") if p.is_file())
    print(f"OK: {len(files)} file(s) downloaded to {out_dir}")
    for f in files:
        print(f"  {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
