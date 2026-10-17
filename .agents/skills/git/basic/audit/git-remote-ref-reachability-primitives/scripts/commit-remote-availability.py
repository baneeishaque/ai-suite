#!/usr/bin/env python3
"""Two-tier commit-availability and branch-tracking probe (READ-ONLY).

Resolves whether a commit is reachable from any configured remote, and whether a
branch tracks any upstream, using the two-tier protocol that plain `git branch -r`
cannot express:

  Tier 1 (cached):  `git branch -r --contains <sha>` over FETCHED remote-tracking refs.
  Tier 2 (live):    `git ls-remote --heads <remote>` per configured remote.

An empty Tier 1 result means "in no fetched remote-tracking ref" -- NOT "absent from
the remote". This script always emits that caveat so the verdict is never read as an
absolute negative.

Tier: Tier 1 (Python) per scripting-language-selection-rules.md section 3 (Tier 1 is
the default) and section 4 (subprocess orchestration + JSON verdict assembly) --
stdlib only, no CPU bottleneck, no ecosystem mandate.

Read-only contract: this script NEVER fetches, NEVER pushes, and NEVER mutates any
ref, index, or working tree. It only reads.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Optional

CACHED_CAVEAT = (
    "Cached-ref verdict only. An empty `git branch -r --contains` means the commit is "
    "in no FETCHED remote-tracking ref, not that no remote has it. Re-fetch "
    "(`git fetch --all --prune`) and re-run for absolute certainty; Tier 2 below is "
    "the live check."
)


def run_git(args, cwd=None) -> tuple[int, str, str]:
    """Run a git command, returning (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            env={**os.environ, "PAGER": "cat"},
        )
    except FileNotFoundError:
        return 127, "", "git not found on PATH"
    return proc.returncode, proc.stdout, proc.stderr


def configured_remotes(repo: str) -> list[str]:
    code, out, _ = run_git(["remote"], cwd=repo)
    if code != 0:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def clean_branch_list(raw: str) -> list[str]:
    names = []
    for line in raw.splitlines():
        name = line.replace("*", " ").replace("+", " ").strip()
        name = re.sub(r"\s+", " ", name)
        if not name:
            continue
        # `branch -vv` appends " <sha> <subject>" and "[origin/x: ahead 1]"
        parts = name.split(" ")
        names.append(parts[0])
    return names


def probe_cached(sha: str, repo: str) -> dict:
    code_r, out_r, _ = run_git(["branch", "-r", "--contains", sha], cwd=repo)
    code_a, out_a, _ = run_git(["branch", "-a", "--contains", sha], cwd=repo)
    return {
        "remote_branches_containing": sorted(clean_branch_list(out_r)) if code_r == 0 else [],
        "all_branches_containing": sorted(clean_branch_list(out_a)) if code_a == 0 else [],
        "remote_query_failed": code_r != 0,
    }


def probe_live(sha: str, repo: str, remotes: list[str]) -> list[dict]:
    results = []
    for remote in remotes:
        code, out, err = run_git(["ls-remote", "--heads", remote], cwd=repo)
        if code != 0:
            results.append({"remote": remote, "status": "UNREACHABLE", "detail": err.strip()[:200]})
            continue
        hits = []
        for line in out.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[0] == sha:
                hits.append(parts[1].split("refs/heads/")[-1])
        results.append(
            {
                "remote": remote,
                "status": "PRESENT" if hits else "ABSENT",
                "branches": sorted(hits),
            }
        )
    return results


def probe_tracking(branch: str, repo: str) -> dict:
    signals = {}
    upstream = None

    code, out, _ = run_git(["branch", "-vv"], cwd=repo)
    if code == 0:
        signals["branch_vv_upstream_marker"] = False
        for line in out.splitlines():
            name = line.replace("*", " ").strip()
            if not name:
                continue
            head = name.split(" ")[0]
            if head == branch:
                m = re.search(r"\[([^\]]+)\]", line)
                if m:
                    upstream = m.group(1)
                    signals["branch_vv_upstream_marker"] = True
                break

    code, out, _ = run_git(["status", "--short", "--branch"], cwd=repo)
    if code == 0:
        header = out.splitlines()[0] if out.splitlines() else ""
        signals["status_sb_header"] = header
        signals["status_sb_shows_tracking"] = "..." in header

    code, out, _ = run_git(["config", "--get-regexp", "branch\\.%s\\..*" % re.escape(branch)], cwd=repo)
    signals["branch_config"] = [line for line in out.splitlines() if line.strip()] if code == 0 else []

    return {
        "branch": branch,
        "upstream": upstream,
        "verdict": "TRACKS" if upstream else "TRACKS_NOTHING",
        "signals": signals,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Two-tier commit-availability and branch-tracking probe (read-only)."
    )
    ap.add_argument("--repo", default=".", help="Repository or linked-worktree git dir.")
    ap.add_argument("--sha", required=True, help="Full or unique short commit SHA.")
    ap.add_argument("--branch", default=None, help="Branch to probe for upstream tracking.")
    ap.add_argument("--remotes", default="", help="Comma-separated remotes (default: all configured).")
    ap.add_argument("--no-live", action="store_true", help="Skip the Tier 2 live probe.")
    ap.add_argument("--json", action="store_true", help="Emit JSON (default is JSON).")
    args = ap.parse_args()

    code, out, err = run_git(["rev-parse", "--verify", "%s^{commit}" % args.sha], cwd=args.repo)
    if code != 0:
        print("error: commit not found in %s: %s" % (args.repo, args.sha), file=sys.stderr)
        return 3

    resolved = out.strip()
    remotes = [r.strip() for r in args.remotes.split(",") if r.strip()] or configured_remotes(args.repo)

    cached = probe_cached(resolved, args.repo)
    live = [] if args.no_live else probe_live(resolved, args.repo, remotes)

    if live:
        verdict = "ON_REMOTE_LIVE" if any(r.get("status") == "PRESENT" for r in live) else "NOT_ON_ANY_REMOTE_LIVE"
    else:
        verdict = (
            "ON_REMOTE_CACHED"
            if cached["remote_branches_containing"]
            else "NOT_ON_ANY_REMOTE_CACHED_ONLY"
        )

    payload = {
        "sha": resolved,
        "repo": args.repo,
        "cached": cached,
        "live": live,
        "verdict": verdict,
        "caveat": CACHED_CAVEAT,
        "tracking": probe_tracking(args.branch, args.repo) if args.branch else None,
    }

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())