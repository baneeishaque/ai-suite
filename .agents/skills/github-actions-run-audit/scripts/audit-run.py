#!/usr/bin/env python3
"""audit-run.py — Audit GitHub Actions workflow runs via the `gh` CLI (observation-only).

Emits a single JSON document on stdout describing:
  - the N most recent runs of <workflow>, OR
  - one specific run (by --run-id).

This script is observation-only. For dispatching a workflow, see sibling
skill `github-actions-workflow-dispatch`. For inspecting a workflow's
committed artifact, see base skill `github-repo-commit-fetch`. For
downloading run artifacts, see sibling script `download-artifacts.py`.

Exit codes
----------
    0  audit ran cleanly (whatever the workflow conclusion was)
    1  gh CLI missing / not authenticated / unrecoverable API error
    2  configuration error
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from typing import Any


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def gh(*args: str, check: bool = True) -> str:
    cp = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if check and cp.returncode != 0:
        die(f"gh {' '.join(args)} failed (exit {cp.returncode}): {cp.stderr.strip()}")
    return cp.stdout


def gh_json(*args: str) -> Any:
    out = gh(*args)
    if not out.strip():
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError as e:
        die(f"gh returned non-JSON: {e}\nstdout: {out[:500]}")


def list_runs(repo: str, workflow: str, limit: int) -> list[dict]:
    return gh_json(
        "run", "list", "--repo", repo, "--workflow", workflow,
        "--limit", str(limit),
        "--json", "databaseId,displayTitle,status,conclusion,createdAt,updatedAt,event,headBranch,url",
    ) or []


def view_run(repo: str, run_id: int) -> dict:
    return gh_json(
        "run", "view", str(run_id), "--repo", repo,
        "--json", "databaseId,displayTitle,status,conclusion,createdAt,updatedAt,event,headBranch,url,jobs",
    ) or {}


def main() -> int:
    p = argparse.ArgumentParser(description="Audit GitHub Actions workflow runs (read-only).")
    p.add_argument("--repo", required=True, help="owner/name (workflow-owning repo)")
    p.add_argument("--workflow", help="workflow filename or display name")
    p.add_argument("--run-id", type=int, help="inspect this specific run id")
    p.add_argument("--limit", type=int, default=5, help="recent runs to list (default 5)")
    args = p.parse_args()

    if not args.workflow and not args.run_id:
        die("either --workflow or --run-id is required", 2)
    if shutil.which("gh") is None:
        die("gh CLI not found. See `github-rest-api-fallback`.", 1)

    report: dict[str, Any] = {"repo": args.repo}

    if args.run_id:
        report["run"] = view_run(args.repo, args.run_id)
    elif args.workflow:
        runs = list_runs(args.repo, args.workflow, args.limit)
        report["recent_runs"] = runs
        if runs:
            report["latest_run"] = view_run(args.repo, runs[0]["databaseId"])

    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
