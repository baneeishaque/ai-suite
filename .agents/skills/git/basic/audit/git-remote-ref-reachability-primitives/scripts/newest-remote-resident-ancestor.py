#!/usr/bin/env python3
"""Newest ancestor of a branch that is already resident in ANY remote (READ-ONLY).

Enumerates the local-only commits of a branch with `git rev-list <branch> --not
--remotes`, then resolves the boundary commit -- the parent of the OLDEST local-only
commit -- and reports which remote branches carry it. This answers "what is the last
commit of my branch that is already backed up / recoverable from a remote?".

Every existing rev-list use in this repository is strictly pairwise two-branch
(`branchA --not branchB`); this script is the multi-remote branch-boundary sweep.

Verdicts:
  HEAD_REMOTE_RESIDENT        - the branch tip itself is already in a remote.
  NEWEST_REMOTE_RESIDENT      - a boundary commit was resolved and is carried by >=1 remote branch.
  NO_REMOTE_RESIDENT_ANCESTOR - the entire branch history is local-only (boundary is the root commit).

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
import subprocess
import sys

CACHED_CAVEAT = (
    "`--not --remotes` subtracts FETCHED remote-tracking refs. A commit classified as "
    "local-only here may still exist on a remote that has not been fetched. Re-fetch "
    "(`git fetch --all --prune`) and re-run before relying on this boundary for a "
    "destructive decision."
)


def run_git(args, cwd=None):
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


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Newest remote-resident ancestor of a branch (read-only)."
    )
    ap.add_argument("--repo", default=".", help="Repository or linked-worktree git dir.")
    ap.add_argument("--branch", required=True, help="Branch, tag, or any rev to walk.")
    ap.add_argument("--json", action="store_true", help="Emit JSON (default is JSON).")
    args = ap.parse_args()

    code, out, _ = run_git(["rev-parse", "--verify", "%s^{commit}" % args.branch], cwd=args.repo)
    if code != 0:
        print("error: cannot resolve rev: %s" % args.branch, file=sys.stderr)
        return 3
    head = out.strip()

    code, out, err = run_git(
        ["log", "--format=%H%x09%s", args.branch, "--not", "--remotes"], cwd=args.repo
    )
    if code != 0:
        print("error: rev-list sweep failed: %s" % err.strip(), file=sys.stderr)
        return 2

    local_only = []
    for line in out.splitlines():
        if not line.strip():
            continue
        sha, _, subject = line.partition("\t")
        local_only.append({"sha": sha, "subject": subject})

    payload = {
        "branch": args.branch,
        "head": head,
        "local_only_count": len(local_only),
        "local_only_commits": local_only,
        "caveat": CACHED_CAVEAT,
        "boundary_sha": None,
        "boundary_subject": None,
        "boundary_carried_by": [],
        "verdict": None,
    }

    if not local_only:
        payload["verdict"] = "HEAD_REMOTE_RESIDENT"
        print(json.dumps(payload, indent=2))
        return 0

    oldest = local_only[-1]
    code, out, err = run_git(["rev-parse", "--verify", "--quiet", "%s^" % oldest["sha"]], cwd=args.repo)
    if code != 0 or not out.strip():
        payload["verdict"] = "NO_REMOTE_RESIDENT_ANCESTOR"
        payload["oldest_local_only"] = oldest
        print(json.dumps(payload, indent=2))
        return 0

    boundary = out.strip()
    code, out, _ = run_git(["show", "-s", "--format=%s", boundary], cwd=args.repo)
    payload["boundary_sha"] = boundary
    payload["boundary_subject"] = out.strip() if code == 0 else ""

    code, out, _ = run_git(["branch", "-r", "--contains", boundary], cwd=args.repo)
    if code == 0:
        for line in out.splitlines():
            name = line.replace("*", " ").strip()
            if name:
                payload["boundary_carried_by"].append(name)

    payload["verdict"] = "NEWEST_REMOTE_RESIDENT"
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())