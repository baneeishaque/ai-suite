#!/usr/bin/env python3
"""repoint-origin-remotes.py — repoint local clone remotes to new URLs.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib; drives the `git` CLI.

For each clone directory under --clones-root, sets the given remote's URL from
the --url-template ({owner} / {repo} placeholders) and — in --execute mode —
verifies it with `git ls-remote <remote> HEAD`.

Safety: DRY-RUN by default — no `set-url` without --execute.

Usage:
    python3 repoint-origin-remotes.py --clones-root <dir> --new-owner <login> \
        --repos a,b [--remote origin] \
        [--url-template 'https://github.com/{owner}/{repo}.git'] [--execute]

Exit codes:
    0  all clones verified (or all planned in dry-run)
    1  at least one clone failed
    2  usage / configuration error
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

DEFAULT_TEMPLATE = "https://github.com/{owner}/{repo}.git"


def die(msg: str, code: int = 2) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def git(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, encoding="utf-8",
            timeout=timeout,
        )
    except OSError as exc:
        die(f"cannot run git: {exc}")
    except subprocess.TimeoutExpired:
        die("git call timed out")


def load_repos(args: argparse.Namespace) -> list[str]:
    repos: list[str] = []
    if args.repos:
        repos.extend(part.strip() for part in args.repos.split(","))
    if args.repos_file:
        try:
            with open(args.repos_file, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        repos.append(line)
        except OSError as exc:
            die(f"cannot read --repos-file: {exc}")
    seen: set[str] = set()
    unique: list[str] = []
    for repo in repos:
        if repo and repo not in seen:
            seen.add(repo)
            unique.append(repo)
    if not unique:
        die("no repos (use --repos and/or --repos-file)")
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description="Repoint clone remotes.")
    parser.add_argument("--clones-root", required=True,
                        help="directory containing the clones")
    parser.add_argument("--new-owner", required=True,
                        help="owner for the {owner} template placeholder")
    parser.add_argument("--repos", help="comma-separated clone names")
    parser.add_argument("--repos-file", help="file with one clone name per line")
    parser.add_argument("--remote", default="origin", help="remote to repoint")
    parser.add_argument("--url-template", default=DEFAULT_TEMPLATE,
                        help="URL template with {owner}/{repo} placeholders")
    parser.add_argument("--execute", action="store_true",
                        help="actually run set-url (default: dry-run)")
    args = parser.parse_args()

    root = Path(args.clones_root)
    if not root.is_dir():
        die(f"--clones-root is not a directory: {root}")

    repos = load_repos(args)
    failed: list[str] = []

    for repo in repos:
        clone = root / repo
        new_url = args.url_template.format(owner=args.new_owner, repo=repo)

        if not clone.is_dir():
            print(json.dumps({"repo": repo, "path": str(clone),
                              "error": "clone directory not found"}),
                  flush=True)
            failed.append(repo)
            continue

        probe = git(["-C", str(clone), "rev-parse", "--git-dir"])
        if probe.returncode != 0:
            print(json.dumps({"repo": repo, "path": str(clone),
                              "error": "not a git repository"}), flush=True)
            failed.append(repo)
            continue

        old = git(["-C", str(clone), "remote", "get-url", args.remote])
        old_url = old.stdout.strip() if old.returncode == 0 else ""

        if not args.execute:
            print(json.dumps({
                "repo": repo, "path": str(clone), "remote": args.remote,
                "old_url": old_url, "new_url": new_url, "dry_run": True,
            }), flush=True)
            continue

        set_url = git(["-C", str(clone), "remote", "set-url",
                       args.remote, new_url])
        if set_url.returncode != 0:
            print(json.dumps({"repo": repo, "path": str(clone),
                              "error": "set-url failed",
                              "detail": set_url.stderr.strip()[:200]}),
                  flush=True)
            failed.append(repo)
            continue

        ls_remote = git(["-C", str(clone), "ls-remote", args.remote, "HEAD"],
                        timeout=120)
        head_sha = ""
        if ls_remote.returncode == 0 and ls_remote.stdout.strip():
            head_sha = ls_remote.stdout.split()[0]
        verified = bool(head_sha)
        record = {"repo": repo, "path": str(clone), "remote": args.remote,
                  "old_url": old_url, "new_url": new_url,
                  "head_sha": head_sha, "verified": verified}
        if not verified:
            record["detail"] = ls_remote.stderr.strip()[:200]
            failed.append(repo)
        print(json.dumps(record), flush=True)

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
