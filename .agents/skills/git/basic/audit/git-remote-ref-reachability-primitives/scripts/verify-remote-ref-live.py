#!/usr/bin/env python3
"""Live EXISTS/ABSENT probe for a single remote branch (READ-ONLY).

Wraps `git ls-remote --heads <remote> <branch>` into an explicit PRESENT/ABSENT
verdict with an optional expectation gate. Use it to PROVE a remote-side mutation
landed (a push, a delete) rather than trusting local remote-tracking refs, which only
update on a fetch.

Read-only contract: this script NEVER fetches, NEVER pushes, and NEVER mutates any
ref, index, or working tree. It only reads.

Tier: Tier 1 (Python) per scripting-language-selection-rules.md section 3 (Tier 1 is
the default) and section 4 (subprocess orchestration + JSON verdict assembly) --
stdlib only, no CPU bottleneck, no ecosystem mandate.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


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
        description="Live EXISTS/ABSENT probe for one remote branch (read-only)."
    )
    ap.add_argument("--repo", default=".", help="Repository or linked-worktree git dir.")
    ap.add_argument("--remote", required=True, help="Remote name.")
    ap.add_argument("--branch", required=True, help="Remote branch name (without refs/heads/).")
    ap.add_argument(
        "--expect",
        choices=["present", "absent"],
        default=None,
        help="Exit 1 when the observed state contradicts this expectation.",
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON (default is JSON).")
    args = ap.parse_args()

    code, out, err = run_git(
        ["ls-remote", "--heads", args.remote, args.branch], cwd=args.repo
    )
    if code != 0:
        print("error: remote not reachable: %s (%s)" % (args.remote, err.strip()[:200]), file=sys.stderr)
        return 2

    matches = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == "refs/heads/%s" % args.branch:
            matches.append({"sha": parts[0], "ref": parts[1]})

    status = "PRESENT" if matches else "ABSENT"
    payload = {
        "remote": args.remote,
        "branch": args.branch,
        "status": status,
        "matches": matches,
        "exit_hint": "ls-remote prints nothing for a branch the remote does not have",
    }
    print(json.dumps(payload, indent=2))

    if args.expect == "present" and status != "PRESENT":
        return 1
    if args.expect == "absent" and status != "ABSENT":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())