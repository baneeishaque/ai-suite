#!/usr/bin/env python3
"""trigger-workflow.py — Trigger a GitHub Actions workflow and (optionally) wait for it.

Wraps `gh workflow run <workflow> --repo <repo>` and, when `--wait` is set,
polls `gh run list` until the freshly-triggered run reaches completed
status, then prints its JSON.

Exit codes
----------
    0  triggered (and, if --wait, run completed regardless of conclusion)
    1  gh missing / dispatch failed / wait timed out
    2  config error
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def gh(*args: str, check: bool = True) -> str:
    cp = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if check and cp.returncode != 0:
        die(f"gh {' '.join(args)} failed: {cp.stderr.strip()}", 1)
    return cp.stdout


def list_recent(repo: str, workflow: str, limit: int = 5) -> list[dict]:
    out = gh(
        "run", "list", "--repo", repo, "--workflow", workflow,
        "--limit", str(limit),
        "--json", "databaseId,status,conclusion,createdAt,event,headBranch,url",
    )
    return json.loads(out) if out.strip() else []


def main() -> int:
    p = argparse.ArgumentParser(description="Trigger a workflow and optionally wait.")
    p.add_argument("--repo", required=True, help="owner/name")
    p.add_argument("--workflow", required=True, help="workflow filename or display name")
    p.add_argument("--ref", help="branch / tag / sha to dispatch against")
    p.add_argument("--field", action="append", default=[], help="key=value workflow_dispatch input (repeatable)")
    p.add_argument("--wait", type=int, default=0, help="seconds to wait for completion (default 0 = fire-and-forget)")
    p.add_argument("--poll", type=int, default=10, help="poll interval seconds (default 10)")
    args = p.parse_args()

    if shutil.which("gh") is None:
        die("gh CLI not found. See `github-rest-api-fallback`.", 1)

    before = {r["databaseId"] for r in list_recent(args.repo, args.workflow)}

    cmd = ["workflow", "run", args.workflow, "--repo", args.repo]
    if args.ref:
        cmd += ["--ref", args.ref]
    for f in args.field:
        cmd += ["--field", f]
    gh(*cmd)

    report: dict = {"repo": args.repo, "workflow": args.workflow, "triggered": True}

    if args.wait > 0:
        deadline = time.time() + args.wait
        new_run = None
        while time.time() < deadline:
            for r in list_recent(args.repo, args.workflow):
                if r["databaseId"] not in before:
                    new_run = r
                    if r["status"] == "completed":
                        report["run"] = r
                        json.dump(report, sys.stdout, indent=2)
                        sys.stdout.write("\n")
                        return 0
                    break
            time.sleep(args.poll)
        report["run"] = new_run
        report["timed_out"] = True
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
        die("timed out waiting for run completion", 1)

    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
