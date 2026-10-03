# !/usr/bin/env python3
"""plan-commit-edit.py — plan an isolated-worktree commit edit (drop / edit / reword).

Deterministic discovery half of `git-commit-edit-in-worktree`: validates the
target commit, resolves the rebase base, derives the scratch worktree path and
the backup branch name, and emits the isolation+rebase plan as JSON (or text).
`--mode in-place` instead emits the Mode B plan (branch + pre_tip) for the
dedicated-worktree route delegated to `git-commit-replace-and-replay`.
Consumes the sibling base `git-rebase-drop-noninteractive`'s todo writer by
reporting its absolute path in the plan; the rebase execution itself lives in
`isolate-edit-worktree.sh` (Mode A only).

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §3.

Exit codes:
  0  plan emitted
  1  base script missing, target/base resolution failure, or git error
  2  usage error
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TODO_WRITER = SCRIPT_DIR.parent.parent / "git-rebase-drop-noninteractive" / "scripts" / "write-drop-todo.py"

def git(repo: str, *args: str) -> str:
    env = dict(os.environ)
    env["GIT_PAGER"] = "cat"
    proc = subprocess.run(
        ["git", "-C", repo,*args], check=True, capture_output=True, text=True, env=env
    )
    return proc.stdout

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit the isolated-worktree rebase plan for editing a commit."
    )
    parser.add_argument("--repo", default=".", help="Repo root (default: current working directory).")
    parser.add_argument("target_sha", help="Full or abbreviated commit SHA to edit.")
    parser.add_argument("--action", choices=("drop", "edit", "reword"), default="drop",
                        help="Todo action to apply (default: drop).")
    parser.add_argument("--mode", choices=("scratch", "in-place"), default="scratch",
                        help="Isolation mode (default: scratch).")
    parser.add_argument("--purpose", default="", help="Purpose token for branch/worktree naming.")
    parser.add_argument("--json", action="store_true", help="Emit the plan as JSON.")
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    try:
        full_sha = git(repo, "rev-parse", "--verify", f"{args.target_sha}^{{commit}}").strip()
    except subprocess.CalledProcessError:
        print(f"plan-commit-edit: cannot resolve commit: {args.target_sha}", file=sys.stderr)
        return 1

    purpose = args.purpose or full_sha[:12]

    if args.mode == "in-place":
        try:
            branch = git(repo, "symbolic-ref", "--short", "-q", "HEAD").strip()
        except subprocess.CalledProcessError:
            print("plan-commit-edit: detached HEAD — in-place mode requires a checked-out branch",
                  file=sys.stderr)
            return 1
        plan = {
            "mode": "in-place",
            "repo": repo,
            "target_sha": full_sha,
            "action": args.action,
            "branch": branch,
            "backup_branch": f"backup/pre-edit-{purpose}",
            "pre_tip": git(repo, "rev-parse", branch).strip(),
        }
    else:
        if not TODO_WRITER.is_file():
            print(f"plan-commit-edit: base script not found: {TODO_WRITER}", file=sys.stderr)
            return 1
        plan = {
            "mode": "scratch",
            "repo": repo,
            "target_sha": full_sha,
            "action": args.action,
            "base_ref": f"{full_sha}^",
            "branch_name": f"rebase-{purpose}",
            "backup_branch": f"backup/pre-edit-{purpose}",
            "worktree_path": os.path.join(repo, "scratch", f"rebase-{purpose}"),
            "sequence_editor": str(TODO_WRITER),
            "sequence_args": [full_sha] + (["--edit", full_sha] if args.action != "drop" else []),
        }

    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        for key, value in plan.items():
            print(f"{key}: {value}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
