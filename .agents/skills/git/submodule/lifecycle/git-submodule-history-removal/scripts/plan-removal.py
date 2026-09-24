# !/usr/bin/env python3
"""plan-removal.py — emit the complete submodule history-removal plan.

Deterministic discovery half of `git-submodule-history-removal`: consumes
the sibling base `git-submodule-history-classification` (submodule list +
commit classification), resolves the drop list (INTRO + all POINTER-UPDATE
commits), and emits every gate command with resolved absolute paths,
including the refresh-1 audited cleanup set and the refresh-2 baseline
verification commands.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §3.

Exit codes:
  0  plan emitted
  1  base script missing, submodule path missing, or git error
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
CLASSIFIER = (
    SCRIPT_DIR.parents[2] / "repair" / "git-submodule-history-classification" / "scripts" / "classify-submodule-commits.py"
)
LISTER = (
    SCRIPT_DIR.parents[2] / "repair" / "git-submodule-history-classification" / "scripts" / "list-submodules.py"
)
PLANNER = (
    SCRIPT_DIR.parents[3] / "basic" / "edit" / "git-commit-edit-in-worktree" / "scripts" / "plan-commit-edit.py"
)
TODO_WRITER = (
    SCRIPT_DIR.parents[3] / "basic" / "edit" / "git-rebase-drop-noninteractive" / "scripts" / "write-drop-todo.py"
)
ISOLATOR = (
    SCRIPT_DIR.parents[3] / "basic" / "edit" / "git-commit-edit-in-worktree" / "scripts" / "isolate-edit-worktree.sh"
)

def git(repo: str, *args: str) -> str:
    env = dict(os.environ)
    env["GIT_PAGER"] = "cat"
    proc = subprocess.run(
        ["git", "-C", repo,*args], check=True, capture_output=True, text=True, env=env
    )
    return proc.stdout

def run_script(script: Path, *args: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(script),*args], check=True, capture_output=True, text=True
    )
    return proc.stdout

def run_script_jsonl(script: Path, *args: str) -> list:
    return [json.loads(line) for line in run_script(script,*args).splitlines() if line.strip()]

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit the submodule history-removal plan (classification + gate commands)."
    )
    parser.add_argument("--repo", default=".", help="Repo root (default: current working directory).")
    parser.add_argument("--path", required=True, help="Submodule path inside the repo (e.g. vendor/lib).")
    parser.add_argument("--json", action="store_true", help="Emit the plan as JSON.")
    args = parser.parse_args()

    for script, label in (
        (CLASSIFIER, "classify-submodule-commits.py"),
        (LISTER, "list-submodules.py"),
        (PLANNER, "plan-commit-edit.py"),
        (TODO_WRITER, "write-drop-todo.py"),
        (ISOLATOR, "isolate-edit-worktree.sh"),
    ):
        if not script.is_file():
            print(f"plan-removal: base script not found: {script} ({label})", file=sys.stderr)
            return 1

    repo = os.path.abspath(args.repo)
    path = args.path
    slug = path.replace("/", "-")

    submodules = run_script_jsonl(LISTER, "--repo", repo, "--json")
    matching = [s for s in submodules if s.get("path") == path]
    if not matching:
        print(
            f"plan-removal: submodule not registered: {path} "
            f"(checked {len(submodules)} gitmodules entries)",
            file=sys.stderr,
        )
        return 1
    entry = matching[0]

    commits = run_script_jsonl(CLASSIFIER, "--repo", repo, "--path", path, "--scope", "all", "--json")
    intros = [c for c in commits if c.get("class") == "INTRO"]
    pointers = [c for c in commits if c.get("class") == "POINTER-UPDATE"]
    mixed = [c for c in commits if c.get("class") == "MIXED"]

    seen: set = set()
    drop_list: list = []
    for c in intros + pointers:
        if c["sha"] not in seen:
            seen.add(c["sha"])
            drop_list.append(c)

    base_ref = f"{intros[0]['sha']}^" if intros else "HEAD^"
    drop_shas = " ".join(c["sha"] for c in drop_list)

    gates = [
        {
            "name": "classify",
            "label": "Pre-classify the path's commit ancestry",
            "command": f"python3 {CLASSIFIER} --repo {repo} --path {path} --scope all --json",
            "expected": (
                f"{len(commits)} commits; {len(drop_list)} to drop "
                f"(INTRO x{len(intros)} + POINTER-UPDATE x{len(pointers)})"
            ),
        },
        {
            "name": "plan",
            "label": "Emit the isolation plan (first drop commit; repeat per drop SHA)",
            "command": (
                f"python3 {PLANNER} --repo {repo} --action drop --purpose {slug} "
                f"{intros[0]['sha'] if intros else ''}"
            ),
            "expected": "worktree path + sequence editor resolved; todo scrub = the drop SHAs above",
        },
        {
            "name": "safety",
            "label": "Backup branch + isolated worktree add",
            "command": (
                f"git -C {repo} branch backup/removal-{slug} && "
                f"git -C {repo} worktree add -b rebase-{slug} {repo}/scratch/rebase-{slug} HEAD"
            ),
            "expected": "backup branch at HEAD; worktree registered",
        },
        {
            "name": "isolate",
            "label": "Scripted rebase inside the isolated worktree",
            "command": (
                f"bash {ISOLATOR} "
                f"--repo {repo} --worktree-path {repo}/scratch/rebase-{slug} --branch rebase-{slug} "
                f"--base-ref {base_ref} --target-sha {drop_shas} --sequence-editor {TODO_WRITER}"
            ),
            "expected": "new tip printed; zero commits touching the path in the rewritten history",
        },
        {
            "name": "refresh1",
            "label": "Refresh-1 audited cleanup set (worktree, branches, path remnant)",
            "command": (
                f"git -C {repo} worktree remove {repo}/scratch/rebase-{slug} --force 2>/dev/null; "
                f"git -C {repo} branch -D rebase-{slug} backup/removal-{slug}; "
                f"rm -rf {os.path.join(repo, path)}"
            ),
            "expected": "no worktree registration, no backup/rebase branches, no path remnant",
        },
        {
            "name": "verify",
            "label": "Refresh-2 baseline verification (zero classification + untouched worktree)",
            "command": f"python3 {CLASSIFIER} --repo {repo} --path {path} --scope all --json | wc -l",
            "expected": "0 commits touching the path after the rewrite; pre/post index + untracked evidence identical",
        },
    ]

    plan = {
        "repo": repo,
        "path": path,
        "url": entry.get("url"),
        "registered": True,
        "intros": intros,
        "pointer_updates": pointers,
        "mixed_commits": mixed,
        "drop_list": drop_list,
        "cleanup_set": [
            f"git worktree remove {repo}/scratch/rebase-{slug} --force",
            f"git branch -D rebase-{slug} backup/removal-{slug}",
            f"rm -rf {os.path.join(repo, path)}",
            ".gitmodules section removal (delegate git-submodule-removal)",
        ],
        "gates": gates,
    }

    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print(f"repo: {repo}")
        print(f"path: {path}")
        print(f"url: {entry.get('url')}")
        print(f"intros: {len(intros)}  pointers: {len(pointers)}  mixed: {len(mixed)}")
        for c in drop_list:
            print(f"drop: {c['sha'][:12]} {c.get('subject', '')}")
        for gate in gates:
            print(f"\n[{gate['name']}] {gate['label']}")
            print(f"  cmd: {gate['command']}")
            print(f"  expected: {gate['expected']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
