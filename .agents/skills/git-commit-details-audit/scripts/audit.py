import argparse
import subprocess
import os
import sys
import re

def run_git(args, cwd=None):
    """Run a git command and return the output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, "PAGER": "cat"}
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_references_for_sha(sha, path):
    """Identify branches and tags containing the SHA, along with their current tips."""
    references = []
    
    # 1. Audit Branches
    branches_raw = run_git(["branch", "-a", "--contains", sha], cwd=path)
    if branches_raw:
        for line in branches_raw.splitlines():
            # Clean up the branch name (remove * and whitespace)
            branch = line.replace("*", "").strip()
            if branch:
                tip = run_git(["rev-parse", branch], cwd=path)
                references.append({
                    "type": "Branch",
                    "name": branch,
                    "tip": tip or "Unknown"
                })
    
    # 2. Audit Tags
    tags_raw = run_git(["tag", "--contains", sha], cwd=path)
    if tags_raw:
        for line in tags_raw.splitlines():
            tag = line.strip()
            if tag:
                tip = run_git(["rev-parse", tag], cwd=path)
                references.append({
                    "type": "Tag",
                    "name": tag,
                    "tip": tip or "Unknown"
                })
                
    return references

def format_commit_details(sha, path, repo_display_name):
    """Format the commit details into the required industrial template."""
    # Metadata: Author, AuthorDate, Committer, CommitterDate, Full Message
    metadata = run_git([
        "show", "-s",
        "--format=Author: %an <%ae>%nAuthorDate: %aD%nCommitter: %cn <%ce>%nCommitDate: %cD%nMessage: %B",
        sha
    ], cwd=path)

    if not metadata:
        return "Error: Could not retrieve commit metadata."

    # Reference Audit (Branches & Tags)
    references = get_references_for_sha(sha, path)

    # Changed Files Inventory
    name_status = run_git(["show", "--name-status", "--format=", sha], cwd=path)

    # Full Hunks (Diffs)
    hunks = run_git(["show", "-p", "--format=", sha], cwd=path)

    # Repository name (folder basename)
    repo_name = os.path.basename(os.path.abspath(path))
    if path == ".":
        repo_name = os.path.basename(os.getcwd())

    output = []
    output.append(f"Repository: {repo_display_name}")
    output.append(f"Commit SHA: {sha}")

    # Split metadata into sections
    meta_lines = metadata.splitlines()
    author        = meta_lines[0]
    author_date   = meta_lines[1]
    committer     = meta_lines[2]
    commit_date   = meta_lines[3]
    message       = "\n".join(meta_lines[4:]).replace("Message: ", "", 1).strip()

    output.append(f"Commit Message: {message}")
    output.append(author)
    output.append(author_date)
    output.append(committer)
    output.append(commit_date)
    
    output.append("-" * 40)
    output.append("### REFERENCE AUDIT (Containing Branches & Tags)")
    if references:
        output.append(f"| Type | Name | Current Tip (HEAD) | Status |")
        output.append(f"| :--- | :--- | :--- | :--- |")
        for ref in references:
            status = "Diverged" if ref["tip"] != sha else "Current"
            output.append(f"| {ref['type']} | {ref['name']} | {ref['tip'][:8]} | {status} |")
    else:
        output.append("No active branches or tags contain this commit.")

    output.append("-" * 40)
    output.append("### CHANGED FILES INVENTORY")
    if name_status:
        output.append(name_status)
    else:
        output.append("No files modified (potential merge or empty commit).")
    
    output.append("-" * 40)
    output.append("### HUNK EXPOSURE (DIFFS)")
    if hunks:
        output.append(f"```diff\n{hunks}\n```")
    else:
        output.append("No hunks available.")

    return "\n".join(output)

def find_repo_for_sha(sha, explicit_repo=None):
    """Find the repository (main or submodule) that contains the SHA.

    When `explicit_repo` is given it is authoritative: the caller is targeting a
    specific checkout (notably a linked worktree's git dir, such as
    .git/modules-worktrees/<name>), which is reachable neither from the process
    CWD nor by enumerating .gitmodules. Discovery is skipped entirely so a
    miss reports against that target instead of silently falling back.
    """
    if explicit_repo:
        if not os.path.isdir(explicit_repo):
            return None, None
        if run_git(["rev-parse", "--quiet", "--verify", f"{sha}^{{commit}}"], cwd=explicit_repo):
            return explicit_repo, f"Explicit repo ({explicit_repo})"
        return None, None

    # 1. Check main repository
    if run_git(["rev-parse", "--quiet", "--verify", f"{sha}^{{commit}}"]):
        return ".", "Main Repository (ai-suite)"
    
    # 2. Check submodules
    submodule_paths = []
    if os.path.exists(".gitmodules"):
        # Extract paths using git config to avoid manual parsing
        output = run_git(["config", "--file", ".gitmodules", "--get-regexp", "path"])
        if output:
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    submodule_paths.append(parts[1])
    
    for path in submodule_paths:
        if os.path.isdir(path):
            # Check if SHA exists in this submodule
            if run_git(["rev-parse", "--quiet", "--verify", f"{sha}^{{commit}}"], cwd=path):
                return path, f"Submodule ({path})"
                
    return None, None

def main():
    parser = argparse.ArgumentParser(
        description="Audit commit metadata, references, changed files, and hunks."
    )
    parser.add_argument("sha", help="Full or unique short commit SHA.")
    parser.add_argument(
        "--repo",
        default=None,
        help="Repository or linked-worktree git dir to audit against. Defaults to "
             "the current working directory plus .gitmodules submodules.",
    )
    args = parser.parse_args()

    sha = args.sha
    path, display_name = find_repo_for_sha(sha, args.repo)

    if not path:
        target = args.repo if args.repo else "the main repository or any submodules"
        print(f"Error: Commit SHA '{sha}' not found in {target}.")
        sys.exit(1)

    print(format_commit_details(sha, path, display_name))

if __name__ == "__main__":
    main()
