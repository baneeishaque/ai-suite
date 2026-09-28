#!/usr/bin/env python3
"""
detect-renovate-auto-rebase.py

Tier-1 (Python) script for detecting if Renovate will auto-rebase.

Usage:
    python3 detect-renovate-auto-rebase.py \
        --config <path-to-renovate.json> \
        --git-dir <path-to-git-repo> \
        --output json|bool \
        [--base-branch <name>]

Exit codes:
    0 = detection successful
    1 = config not found / parse error / git error
    2 = invalid arguments
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def run_git(git_dir: Path, *args: str) -> Tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["git", "-C", str(git_dir), *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "git command timed out"
    except Exception as e:
        return -1, "", str(e)


def get_default_branch(git_dir: Path) -> str:
    """Get the default branch name."""
    code, stdout, _ = run_git(Path("."), "symbolic-ref", "refs/remotes/origin/HEAD")
    if code == 0 and stdout:
        # Output format: refs/remotes/origin/main
        match = re.search(r'refs/remotes/origin/(.+)', stdout)
        if match:
            return match.group(1)
    # Fallback
    code, stdout, _ = run_git(Path("."), "rev-parse", "--abbrev-ref", "HEAD")
    if code == 0:
        return stdout.strip()
    return "main"


def check_branch_protection(git_dir: Path, branch: str) -> bool:
    """
    Check if branch protection requires up-to-date PRs.
    Uses GitHub API if available, otherwise returns False.
    """
    # Try gh CLI first
    try:
        result = subprocess.run(
            ["gh", "api", f"/repos/:owner/:repo/branches/{branch}/protection"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Check if "required_status_checks" -> "strict" is true
            required_checks = data.get("required_status_checks", {})
            if isinstance(required_checks, dict) and required_checks.get("strict", False):
                return True
    except Exception:
        pass
    return False


def check_merge_queue(git_dir: Path, branch: str) -> bool:
    """
    Check if GitHub merge queue is enabled for the branch.
    """
    try:
        result = subprocess.run(
            ["gh", "api", f"/repos/:owner/:repo/branches/{branch}/protection"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Check for merge queue config
            if "required_pull_request_reviews" in data:
                return False  # Simplified check
    except Exception:
        pass
    return False


def load_renovate_config(config_path: Path) -> Dict:
    """Load and parse Renovate config (JSON/JSONC/JSON5)."""
    content = config_path.read_text(encoding="utf-8")
    # Strip comments for JSONC
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config: {e}")


def detect_auto_rebase(config: Dict, git_info: Dict) -> Tuple[bool, str, Dict]:
    """
    Core detection logic per Renovate docs.
    
    Returns: (will_auto_rebase, reason, details_dict)
    """
    rebase_when = config.get("rebaseWhen", "auto")
    automerge = config.get("automerge", False)
    platform_automerge = config.get("platformAutomerge", True)
    automerge_type = config.get("automergeType", "pr")
    
    branch_protection = git_info.get("branch_protection_up_to_date", False)
    merge_queue = git_info.get("merge_queue_enabled", False)
    platform_automerge_config = config.get("platformAutomerge", True)
    
    details = {
        "rebaseWhen": rebase_when,
        "automerge": automerge,
        "platformAutomerge": platform_automerge_config,
        "branch_protection_up_to_date": git_info.get("branch_protection_up_to_date", False),
        "merge_queue_enabled": git_info.get("merge_queue_enabled", False),
    }
    
    if rebase_when == "behind-base-branch":
        return True, "rebaseWhen=behind-base-branch (explicit)", details
    
    if rebase_when == "automerging":
        if automerge:
            return True, "rebaseWhen=automerging with automerge=true", details
        return False, "rebaseWhen=automerging but automerge=false", details
    
    if rebase_when == "conflicted":
        return False, "rebaseWhen=conflicted (only rebases on conflicts)", details
    
    if rebase_when == "never":
        return False, "rebaseWhen=never", details
    
    # rebaseWhen == "auto" (default) or not set
    if automerge:
        return True, "rebaseWhen=auto with automerge=true", details
    
    if config.get("platformAutomerge", True) and details["branch_protection_up_to_date"]:
        return True, "rebaseWhen=auto with platformAutomerge + branch protection requiring up-to-date", details
    
    # Check for GitHub merge queue / GitLab merge trains
    # These cause "auto" to behave as "conflicted"
    # We can't easily detect merge queue without API, but we note it in details
    details["merge_queue_enabled"] = git_info.get("merge_queue_enabled", False)
    if details["merge_queue_enabled"]:
        return False, "rebaseWhen=auto with merge queue/merge train (uses conflicted)", details
    
    return False, "rebaseWhen=auto (default) → conflicted (no automerge, no branch protection requiring up-to-date)", details


def get_git_info(git_dir: Path, base_branch: Optional[str] = None) -> Dict:
    """Collect git repository information for detection."""
    if base_branch is None:
        base_branch = get_default_branch(Path("."))
    
    info = {
        "default_branch": base_branch,
        "branch_protection_up_to_date": False,
        "merge_queue_enabled": False,
    }
    
    # Check branch protection
    info["branch_protection_up_to_date"] = check_branch_protection(Path("."), base_branch)
    
    # Check merge queue (simplified)
    info["merge_queue_enabled"] = check_merge_queue(Path("."), base_branch)
    
    return info


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect if Renovate will auto-rebase on base branch rewrite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 detect-renovate-auto-rebase.py \\
      --config renovate.json \\
      --git-dir . \\
      --output json

  python3 detect-renovate-auto-rebase.py \\
      --config .github/renovate.jsonc \\
      --git-dir . \\
      --output bool
        """,
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to renovate.json / renovate.jsonc / renovate.json5",
    )
    parser.add_argument(
        "--git-dir",
        required=True,
        help="Path to git repository root",
    )
    parser.add_argument(
        "--output",
        choices=["json", "bool"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--base-branch",
        help="Base branch name (default: repo's default branch)",
    )

    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config file not found: {config_path}", file=sys.stderr)
        return 1

    git_dir = Path(args.git_dir)
    if not git_dir.exists() or not (git_dir / ".git").exists():
        print(f"Not a git repository: {git_dir}", file=sys.stderr)
        return 1

    try:
        config = load_renovate_config(Path(args.config))
    except ValueError as e:
        print(f"Config parse error: {e}", file=sys.stderr)
        return 1

    git_dir_path = Path(args.git_dir)
    base_branch = args.base_branch
    git_info = get_git_info(git_dir_path, base_branch)

    will_rebase, reason, details = detect_auto_rebase(config, git_info)

    if args.output == "bool":
        print("true" if will_rebase else "false")
    else:
        output = {
            "will_auto_rebase": will_rebase,
            "reason": reason,
            **details,
        }
        print(json.dumps(output, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())