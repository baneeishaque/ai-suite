#!/usr/bin/env python3
"""rebase-personal-on-team.py — Incremental restack of personal branch onto team branch tip.

Usage:
    python3 rebase-personal-on-team.py \\
        --team-branch <team-branch> \\
        --personal-branch <personal-branch> \\
        --repo-path <path>

Exit codes:
    0 — Restack succeeded, personal commits verified at tip.
    1 — Precondition failure.
    2 — Restack failed (rebase error or conflict).
    3 — Post-restack verification failed.
"""

import argparse
import subprocess
import sys
import time
from datetime import date
from pathlib import Path


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def run_git(repo_path: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo_path), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def check_preconditions(repo_path: Path, team_branch: str, personal_branch: str) -> bool:
    # Both branches must exist
    for branch in (team_branch, personal_branch):
        result = run_git(repo_path, ["rev-parse", "--verify", branch], check=False)
        if result.returncode != 0:
            eprint(f"ERROR: branch '{branch}' does not exist")
            return False

    # Working tree must be clean
    result = run_git(repo_path, ["status", "--short"], check=False)
    if result.stdout.strip():
        eprint("ERROR: working tree is not clean:")
        eprint(result.stdout)
        return False

    # personal-branch must be a descendant of team-branch (or equal — first-cycle)
    result = run_git(repo_path, ["merge-base", team_branch, personal_branch], check=False)
    if result.returncode != 0:
        eprint("ERROR: cannot find merge-base between branches")
        return False
    merge_base = result.stdout.strip()

    # Verify personal branch contains team branch tip
    result = run_git(repo_path, ["merge-base", "--is-ancestor", team_branch, personal_branch], check=False)
    if result.returncode != 0:
        eprint("WARNING: personal branch is NOT a descendant of team branch.")
        eprint(f"  Team branch tip may have diverged from personal-branch base ({merge_base}).")
        eprint("  Continuing anyway — rebase --onto will re-anchor based on merge-base.")

    return True


def tag_pre_state(repo_path: Path, personal_branch: str) -> str | None:
    today = date.today().isoformat()
    timestamp = str(int(time.time()))
    tag_name = f"backup/personal-pre-restack-{today}-{timestamp}"

    result = run_git(repo_path, ["rev-parse", personal_branch], check=False)
    if result.returncode != 0:
        eprint("ERROR: cannot find personal branch tip")
        return None

    tip_sha = result.stdout.strip()
    result = run_git(repo_path, ["tag", tag_name, tip_sha], check=False)
    if result.returncode != 0:
        eprint(f"ERROR: failed to create backup tag '{tag_name}'")
        eprint(result.stderr)
        return None

    print(f"Created backup tag: {tag_name} -> {tip_sha[:12]}")
    return tag_name


def run_restack(repo_path: Path, team_branch: str, personal_branch: str) -> bool:
    # Find merge-base
    result = run_git(repo_path, ["merge-base", team_branch, personal_branch], check=False)
    if result.returncode != 0:
        eprint("ERROR: cannot find merge-base")
        return False
    merge_base = result.stdout.strip()

    print(f"Merge-base: {merge_base[:12]}")
    print(f"Rebasing {personal_branch} onto {team_branch} (from {merge_base[:12]})...")

    result = run_git(repo_path, [
        "rebase", "--onto", team_branch, merge_base, personal_branch,
    ], check=False)

    if result.returncode != 0:
        eprint("ERROR: rebase failed")
        eprint(result.stderr)
        return False

    print("Rebase completed successfully")
    return True


def verify_personal_at_tip(repo_path: Path, team_branch: str, personal_branch: str) -> bool:
    # Check that personal-branch is now directly on team-branch tip
    result = run_git(repo_path, ["merge-base", "--is-ancestor", team_branch, personal_branch], check=False)
    if result.returncode != 0:
        eprint("ERROR: personal branch is not an ancestor of team branch after restack")
        return False

    # List commits that are on personal but not on team
    result = run_git(repo_path, [
        "log", "--oneline", f"{team_branch}..{personal_branch}",
    ], check=False)

    if not result.stdout.strip():
        eprint("ERROR: no personal commits found at tip of personal branch")
        eprint("  The personal branch and team branch are at the same commit.")
        eprint("  Personal commits may have been lost or were no-ops on the new base.")
        return False

    print(f"\nPersonal commits at tip ({result.stdout.count(chr(10)) + 1} commits):")
    print(result.stdout)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Incremental restack of personal branch onto team branch tip")
    parser.add_argument("--team-branch", required=True, help="Team branch name (e.g., main_aes-53)")
    parser.add_argument("--personal-branch", required=True, help="Personal branch name (e.g., personal/skills)")
    parser.add_argument("--repo-path", required=True, help="Path to Git repository")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    team_branch = args.team_branch
    personal_branch = args.personal_branch

    # Step 1: Validate preconditions
    print("=== Checking preconditions ===")
    if not check_preconditions(repo_path, team_branch, personal_branch):
        return 1

    # Step 2: Tag pre-restack state
    print("\n=== Tagging pre-restack state ===")
    tag_name = tag_pre_state(repo_path, personal_branch)
    if tag_name is None:
        return 1

    # Step 3: Run the restack
    print("\n=== Restacking ===")
    if not run_restack(repo_path, team_branch, personal_branch):
        print(f"Recovery: backup tag '{tag_name}' preserved for recovery")
        return 2

    # Step 4: Verify personal commits at tip
    print("\n=== Verifying ===")
    if not verify_personal_at_tip(repo_path, team_branch, personal_branch):
        print(f"Recovery: backup tag '{tag_name}' preserved for recovery")
        return 3

    print(f"=== Restack complete ===")
    print(f"Backup tag: {tag_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
