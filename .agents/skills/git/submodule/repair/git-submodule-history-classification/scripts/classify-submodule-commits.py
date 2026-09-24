# !/usr/bin/env python3
"""classify-submodule-commits.py — classify every commit that touched a submodule path.

For each surviving branch (--exclude-branches glob skip-list, default
entire/*, backup/*, backup2/*), enumerate `git log <branch> -- <path>` and
classify every hit:

  INTRO          adds the gitlink / .gitmodules entry (mode 000000 -> 160000)
  POINTER-UPDATE only the gitlink SHA changed (mode 160000 -> 160000), no other files
  MIXED          touches the path AND other files
  REMOVAL        deletes the gitlink entry (mode 160000 -> 000000)

Read-only. Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §3.

Exit codes:
  0  ok
  2  path never existed in any scanned branch (empty result)
  3  usage error
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys

DEFAULT_EXCLUDES = ["entire/*", "backup/*", "backup2/*"]

_MODE_RE = re.compile(r":(?P<oldmode>[0-9]{6}|-)\s+(?P<newmode>[0-9]{6}|-)\s+\S+\s+\S+\s+[A-Z]\d*\s+(?P<path>.+)")
_NO_MODE_RE = re.compile(r":000000\s+(?P<newmode>[0-9]{6})\s+\S+\s+\S+\s+[A-Z]\d*\s+(?P<path>.+)")

def git(repo: str, *args: str) -> str:
    env = dict(os.environ)
    env["GIT_PAGER"] = "cat"
    proc = subprocess.run(
        ["git", "-C", repo,*args], check=True, capture_output=True, text=True, env=env
    )
    return proc.stdout

def branches(repo: str, excludes: list[str], contains: str | None) -> list[str]:
    raw = git(repo, "branch", "-a", *(["--contains", contains] if contains else []))
    out = []
    for line in raw.splitlines():
        name = line.strip().lstrip("* ")
        if not name or " -> " in name:
            continue
        match_name = name.removeprefix("remotes/")
        if any(fnmatch.fnmatch(match_name, pat) for pat in excludes):
            continue
        if any(fnmatch.fnmatch(name, pat) for pat in excludes):
            continue
        out.append(name)
    return out

def classify(sha: str, repo: str, path: str) -> tuple[str, list[str]]:
    raw_out = git(repo, "show", "--format=", "--raw", sha, "--", path).strip()
    all_files = [
        f for f in git(repo, "show", "--format=", "--name-only", sha).splitlines()
        if f.strip() and not f.startswith("..")
    ]
    others = [f for f in all_files if f not in (path, ".gitmodules")]
    mode = None
    for line in raw_out.splitlines():
        m = _MODE_RE.match(line.strip())
        if m and m.group("path") == path:
            mode = (m.group("oldmode"), m.group("newmode"))
            break
    if mode is None:
        m = _NO_MODE_RE.match(raw_out.strip().splitlines()[0]) if raw_out else None
        if m and m.group("path") == path:
            mode = ("000000", m.group("newmode"))
    if mode is None:
        return ("POINTER-UPDATE", others)
    old, new = mode
    if old == "000000":
        return ("INTRO", others)
    if new == "000000":
        return ("REMOVAL", others)
    if others:
        return ("MIXED", others)
    return ("POINTER-UPDATE", others)

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify every commit that touched a submodule path across branches."
    )
    parser.add_argument("--repo", default=".", help="Repo root (default: current working directory).")
    parser.add_argument("--path", required=True, help="Submodule path relative to the repo root.")
    parser.add_argument(
        "--scope", choices=("all", "commit"), default="all",
        help="all = every branch; commit = only branches containing --contains <sha>.",
    )
    parser.add_argument("--contains", metavar="SHA", help="Candidate SHA for --scope commit.")
    parser.add_argument(
        "--exclude-branches", action="append", default=[], metavar="GLOB",
        help="Branch glob to skip (repeatable; defaults: entire/*, backup/*, backup2/*).",
    )
    parser.add_argument("--first-parent", action="store_true", help="Restrict to first-parent history.")
    parser.add_argument("--json", action="store_true", help="Emit JSONL.")
    args = parser.parse_args()

    if args.scope == "commit" and not args.contains:
        print("classify-submodule-commits: --scope commit requires --contains <sha>", file=sys.stderr)
        return 3

    repo = os.path.abspath(args.repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        print(f"classify-submodule-commits: not a git repository: {repo}", file=sys.stderr)
        return 3

    excludes = args.exclude_branches or DEFAULT_EXCLUDES
    rows = []
    try:
        log_args = ["log", "--format=%H|%s"]
        if args.first_parent:
            log_args.append("--first-parent")
        for branch in branches(repo, excludes, args.contains if args.scope == "commit" else None):
            for line in git(repo, *log_args, branch, "--", args.path).splitlines():
                if "|" not in line:
                    continue
                sha, subject = line.split("|", 1)
                cls, files = classify(sha, repo, args.path)
                rows.append({"sha": sha, "branch": branch, "subject": subject, "class": cls, "files": files})
    except subprocess.CalledProcessError as error:
        print(f"classify-submodule-commits: git error: {error}", file=sys.stderr)
        return 3

    if not rows:
        print(f"classify-submodule-commits: path never existed in any scanned branch: {args.path}", file=sys.stderr)
        return 2

    for r in rows:
        if args.json:
            print(json.dumps(r))
        else:
            print(f"{r['sha']:>12}  {r['branch']:<30}  {r['class']:<15}  {r['subject']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
