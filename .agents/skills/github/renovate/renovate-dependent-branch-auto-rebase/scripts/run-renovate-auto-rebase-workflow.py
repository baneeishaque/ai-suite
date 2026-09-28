#!/usr/bin/env python3
"""
run-renovate-auto-rebase-workflow.py

Tier-1 (Python) composer script for Renovate auto-rebase workflow.

Usage:
    python3 run-renovate-auto-rebase-workflow.py \
        --base-branch <name> \
        --renovate-branches <glob-pattern> \
        --mode auto|manual \
        [--dry-run] \
        [--config-path <path>] \
        [--git-dir <path>]

Exit codes:
    0 = success
    1 = error
    2 = invalid arguments
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def run_cmd(cmd: List[str], cwd: Optional[Path] = None, capture: bool = True) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=capture,
            text=True,
            timeout=120,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "command timed out"
    except Exception as e:
        return -1, "", str(e)


def run_detector(config_path: Path, git_dir: Path) -> Dict:
    """Run the renovate-auto-rebase-detector and return parsed result."""
    cmd = [
        "python3",
        "renovate-auto-rebase-detector/scripts/detect-renovate-auto-rebase.py",
        "--config", str(config_path),
        "--git-dir", str(git_dir),
        "--output", "json",
    ]
    code, stdout, stderr = run_cmd(cmd)
    if code != 0:
        raise RuntimeError(f"Detector failed: {stderr}")
    return json.loads(stdout)


def generate_config(config_path: Path, template: str, params: Dict) -> None:
    """Generate Renovate config using renovate-config-patterns."""
    cmd = [
        "python3",
        "renovate-config-patterns/scripts/generate-renovate-config.py",
        "--template", template,
        "--output", str(config_path),
        "--params", json.dumps(params),
    ]
    code, stdout, stderr = run_cmd(cmd)
    if code != 0:
        raise RuntimeError(f"Config generation failed: {stderr}")


def discover_renovate_branches(git_dir: Path, pattern: str) -> List[str]:
    """Discover Renovate branches matching the glob pattern."""
    # Use git for-each-ref with pattern matching
    cmd = [
        "git", "for-each-ref", "--format=%(refname:short)",
        "refs/heads/renovate/*", "refs/remotes/origin/renovate/*"
    ]
    code, stdout, stderr = run_cmd(cmd, cwd=Path("."))
    if code != 0:
        return []
    
    branches = stdout.strip().split("\n")
    # Filter by pattern (simple glob matching)
    import fnmatch
    return [b for b in branches if fnmatch.fnmatch(b, pattern)]


def get_renovate_branches_tips(git_dir: Path, branches: List[str]) -> Dict[str, str]:
    """Get the tip SHA for each Renovate branch."""
    tips = {}
    for branch in branches:
        code, stdout, _ = run_cmd(["git", "rev-parse", branch], cwd=Path("."))
        if code == 0:
            tips[branch] = stdout.strip()
    return tips


def find_dependents(base_branch: str, old_tip: str, new_tip: str, renovate_branches: List[str]) -> List[str]:
    """Find Renovate branches that are dependents of the base branch move."""
    dependents = []
    for branch in branches:
        # Check if merge-base with new_tip equals old_tip
        code, stdout, _ = run_cmd(["git", "merge-base", branch, new_tip])
        if code == 0 and stdout.strip() == old_tip:
            dependents.append(branch)
    return dependents


def run_cascade(base_branch: str, old_tip: str, new_tip: str, dependents: List[str], dry_run: bool) -> None:
    """Invoke git-dependent-branch-restack-cascade via its PowerShell script."""
    # Convert dependents to PowerShell array format
    deps_ps = ",".join(f'"{d}"' for d in dependents)
    
    ps_script = f"""
$repo = "."
$old = "{old_tip}"
$new = "{new_tip}"
$dependents = @({deps_ps})

foreach ($d in $dependents) {{
    Write-Host "Restacking $d onto $new from $old"
    git -C $repo rebase --onto $new $old $d
    if ($LASTEXITCODE -ne 0) {{
        Write-Error "Rebase failed for $d"
        exit 1
    }}
    if (-not $dry_run) {{
        git push --force-with-lease origin $d
    }}
}}
"""
    cmd = ["pwsh", "-Command", ps_script]
    code, stdout, stderr = run_cmd(cmd)
    if code != 0:
        raise RuntimeError(f"Cascade failed: {stderr}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Renovate auto-rebase workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto mode (default): detect, update config if needed, fallback to cascade
  python3 run-renovate-auto-rebase-workflow.py \\
      --base-branch main \\
      --renovate-branches "renovate/*" \\
      --mode auto \\
      --dry-run

  # Manual mode: always use cascade
  python3 run-renovate-auto-rebase-workflow.py \\
      --base-branch main \\
      --renovate-branches "renovate/*" \\
      --mode manual
        """,
    )
    parser.add_argument("--base-branch", required=True, help="Base branch name (e.g., main)")
    parser.add_argument("--renovate-branches", required=True, help="Glob pattern for Renovate branches (e.g., renovate/*)")
    parser.add_argument("--mode", choices=["auto", "manual"], default="auto", help="Workflow mode (default: auto)")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    parser.add_argument("--config-path", default="renovate.json", help="Path to Renovate config")
    parser.add_argument("--git-dir", default=".", help="Git repository path")

    args = parser.parse_args()

    config_path = Path(args.config_path)
    git_dir = Path(args.git_dir)

    if not config_path.exists():
        print(f"Config not found: {config_path}", file=sys.stderr)
        return 1

    try:
        # Step 1: Detect if Renovate will auto-rebase
        print(f"[1/4] Detecting Renovate auto-rebase behavior...")
        detector_result = run_detector(Path(args.config_path), Path(args.git_dir))
        
        will_rebase = detector_result.get("will_auto_rebase", False)
        reason = detector_result.get("reason", "unknown")
        rebase_when = detector_result.get("rebaseWhen", "auto")
        
        print(f"    Will auto-rebase: {will_rebase}")
        print(f"    Reason: {reason}")
        print(f"    rebaseWhen: {rebase_when}")

        # Step 2: Decide workflow path
        if args.mode == "auto" and will_rebase:
            print(f"[2/4] Renovate will auto-rebase ({reason}). No manual action needed.")
            
            # Verify config has behind-base-branch
            if detector_result.get("rebaseWhen") != "behind-base-branch":
                print(f"[3/4] Config has rebaseWhen={rebase_when}, updating to 'behind-base-branch'...")
                if not args.dry_run:
                    generate_config(
                        Path(args.config_path),
                        "automerge",
                        {
                            "rebaseWhen": "behind-base-branch",
                            "automerge": True,
                            "automergeStrategy": "rebase",
                        }
                    )
                    print("    Config updated with rebaseWhen=behind-base-branch")
                else:
                    print("    [DRY-RUN] Would update config with rebaseWhen=behind-base-branch")
            else:
                print(f"    Config already has rebaseWhen=behind-base-branch")
            
            print(f"[4/4] Done. Renovate will handle auto-rebase on base rewrite.")
            return 0

        # Step 3: Manual cascade needed
        print(f"[2/4] Renovate will NOT auto-rebase ({reason}). Using manual cascade.")
        
        if args.mode == "auto":
            print("    Auto mode: falling back to manual cascade via git-dependent-branch-restack-cascade")
        else:
            print("    Manual mode: using git-dependent-branch-restack-cascade")

        # Step 3: Discover Renovate branches
        print(f"[3/4] Discovering Renovate branches matching '{args.renovate_branches}'...")
        renovate_branches = discover_renovate_branches(Path("."), args.renovate_branches)
        print(f"    Found: {renovate_branches}")

        if not renovate_branches:
            print("    No Renovate branches found. Nothing to do.")
            return 0

        # Step 4: Find dependents (branches rooted on old tip)
        print(f"[4/4] Finding dependents...")
        # We need to know the old tip - for now, use the merge-base of base branch with first renovate branch
        # In practice, this should come from the operation that moved the base branch
        # For now, we'll use a heuristic: the commit before the base branch's current tip
        code, old_tip, _ = run_cmd(["git", "rev-parse", f"{args.base_branch}^"])
        if code != 0:
            print("Could not determine old tip. Please specify manually.", file=sys.stderr)
            return 1
        old_tip = old_tip.strip()
        new_tip = args.base_branch
        
        print(f"    Base branch: {args.base_branch}")
        print(f"    Old tip: {old_tip}")
        print(f"    New tip: {new_tip}")

        dependents = find_dependents(args.base_branch, old_tip, new_tip, renovate_branches)
        print(f"    Dependents: {dependents}")

        if not dependents:
            print("    No dependents found. Nothing to restack.")
            return 0

        if args.dry_run:
            print(f"    [DRY-RUN] Would restack {len(dependents)} dependents:")
            for d in dependents:
                print(f"      git rebase --onto {new_tip} {old_tip} {d}")
            return 0

        # Run cascade
        print(f"    Running git-dependent-branch-restack-cascade...")
        run_cascade(args.base_branch, old_tip, new_tip, dependents, args.dry_run)
        print("    Cascade completed successfully!")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())