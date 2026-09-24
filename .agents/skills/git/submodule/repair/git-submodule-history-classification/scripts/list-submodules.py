# !/usr/bin/env python3
"""list-submodules.py — enumerate registered submodules with remote URLs and status.

Replicates the inventory workflow behind `docs/uninitialized-submodules.md`:
`git submodule status` for the status flag, `git ls-files --stage` for the
exact gitlink paths/SHAs, and `.gitmodules` for the name -> path -> url triple.

Read-only. Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §3.

Exit codes:
  0  success
  2  usage / git error
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

STATUS_NAMES = {" ": "initialized", "-": "uninitialized", "+": "plus", "U": "conflict"}

def git(repo: str, *args: str) -> str:
    env = dict(os.environ)
    env["GIT_PAGER"] = "cat"
    proc = subprocess.run(
        ["git", "-C", repo,*args], check=True, capture_output=True, text=True, env=env
    )
    return proc.stdout

def discover(repo: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    for line in git(repo, "ls-files", "--stage").splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        meta, path = parts
        fields = meta.split(" ")
        if len(fields) >= 3 and fields[0] == "160000":
            links.append({"path": path, "sha": fields[1]})

    name_by_path: dict[str, str] = {}
    url_by_name: dict[str, str] = {}
    for line in git(repo, "config", "-f", os.path.join(repo, ".gitmodules"), "--get-regexp", r"^submodule\..*\.path$").splitlines():
        key, _, value = line.partition(" ")
        name = key[len("submodule."):-len(".path")]
        name_by_path[value.strip()] = name
    for name in set(name_by_path.values()):
        try:
            url = git(repo, "config", "-f", os.path.join(repo, ".gitmodules"), "--get", f"submodule.{name}.url").strip()
        except subprocess.CalledProcessError:
            url = ""
        url_by_name[name] = url

    status_lines = git(repo, "submodule", "status").splitlines()

    rows: list[dict[str, str]] = []
    for link in links:
        path = link["path"]
        name = name_by_path.get(path, path)
        flag = "-"
        for line in status_lines:
            rest = line[1:].strip()
            if rest.split(" (")[0].endswith(path):
                flag = line[0]
                break
        rows.append({
            "name": name,
            "path": path,
            "url": url_by_name.get(name, ""),
            "status": STATUS_NAMES.get(flag, "uninitialized"),
        })
    return rows

def main() -> int:
    parser = argparse.ArgumentParser(
        description="List registered submodules with name, path, remote URL, and status."
    )
    parser.add_argument("--repo", default=".", help="Repo root (default: current working directory).")
    parser.add_argument(
        "--uninitialized-only", action="store_true",
        help="Only output submodules whose status is 'uninitialized'.",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit JSONL (default: TSV name<TAB>path<TAB>url<TAB>status).",
    )
    parser.add_argument(
        "--report", metavar="PATH",
        help="Write a markdown table report to PATH instead of stdout.",
    )
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        print(f"list-submodules: not a git repository: {repo}", file=sys.stderr)
        return 2

    try:
        rows = discover(repo)
    except subprocess.CalledProcessError as error:
        print(f"list-submodules: git error: {error}", file=sys.stderr)
        return 2

    if args.uninitialized_only:
        rows = [r for r in rows if r["status"] == "uninitialized"]
    rows.sort(key=lambda r: r["path"])

    if args.report:
        lines = ["# Uninitialized Submodules", "",
                 "Registered Git submodules in the parent repository. Each row lists the submodule",
                 "name, its path inside the repository, and the remote URL it tracks.",
                 "", "> Generated via `git submodule status` + `git config -f .gitmodules`.",
                 "", "| Submodule | Path | Remote URL |", "| --- | --- | --- |"]
        for i, r in enumerate(rows, 1):
            lines.append(f"| {r['name']} | {r['path']} | {r['url']} |")
        Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 0

    for r in rows:
        if args.json:
            print(json.dumps(r))
        else:
            print("\t".join([r["name"], r["path"], r["url"], r["status"]]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
