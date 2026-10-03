#!/usr/bin/env python3
"""worktree-state-fingerprint.py — capture and compare byte-level Git worktree state.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §3 —
subprocess-orchestrated, pure-stdlib state capture; no pip dependencies.

Subcommands:
  capture  --repo <path> --out <snapshot.json>
  compare  --pre <a.json> --post <b.json> [--json]

The capture hashes the raw stdout bytes of four git commands — byte-for-byte
compatible with the shell pipeline it replaces:
  git ls-files -s | shasum -a 256
  git diff --cached --binary | shasum -a 256
  git diff --binary | shasum -a 256
  git ls-files --others --exclude-standard | shasum -a 256
plus the raw `git status --porcelain` text, HEAD, and the commit count.

compare reports every delta field-by-field. It NEVER applies tolerances —
the expected-delta policy belongs to the consuming skill (see the composer
`git-commit-edit-in-worktree` gates for the reference policy).

Exit codes:
  0  capture ok / compare: snapshots identical
  1  compare: one or more deltas found
  2  usage, I/O, or git error
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HASH_FIELDS = ("index", "staged_diff", "worktree_diff", "untracked")

def _git(repo: str, *args: str) -> bytes:
    env = dict(os.environ)
    env["GIT_PAGER"] = "cat"
    proc = subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, env=env
    )
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git {' '.join(args)} failed in {repo}: {detail}")
    return proc.stdout

def capture(repo: str, out_path: str) -> int:
    repo_abs = os.path.abspath(repo)
    if not os.path.isdir(repo_abs):
        print(f"worktree-state-fingerprint: repo not found: {repo_abs}", file=sys.stderr)
        return 2
    snapshot = {
        "schema_version": 1,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "repo": repo_abs,
        "head": _git(repo_abs, "rev-parse", "HEAD").decode().strip(),
        "commit_count": int(
            _git(repo_abs, "rev-list", "--count", "HEAD").decode().strip()
        ),
        "porcelain": _git(repo_abs, "status", "--porcelain").decode(
            "utf-8", errors="surrogateescape"
        ),
        "hashes": {
            "index": hashlib.sha256(_git(repo_abs, "ls-files", "-s")).hexdigest(),
            "staged_diff": hashlib.sha256(
                _git(repo_abs, "diff", "--cached", "--binary")
            ).hexdigest(),
            "worktree_diff": hashlib.sha256(
                _git(repo_abs, "diff", "--binary")
            ).hexdigest(),
            "untracked": hashlib.sha256(
                _git(repo_abs, "ls-files", "--others", "--exclude-standard")
            ).hexdigest(),
        },
    }
    Path(out_path).write_text(
        json.dumps(snapshot, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "worktree-state-fingerprint: captured "
        f"{repo_abs} @ {snapshot['head'][:12]} -> {out_path}"
    )
    return 0

def _collect_deltas(pre: dict, post: dict) -> list[dict]:
    deltas: list[dict] = []
    for field in ("head", "commit_count", "porcelain"):
        if pre.get(field) != post.get(field):
            deltas.append(
                {"field": field, "pre": pre.get(field), "post": post.get(field)}
            )
    pre_hashes = pre.get("hashes") or {}
    post_hashes = post.get("hashes") or {}
    for field in HASH_FIELDS:
        if pre_hashes.get(field) != post_hashes.get(field):
            deltas.append(
                {
                    "field": f"hashes.{field}",
                    "pre": pre_hashes.get(field),
                    "post": post_hashes.get(field),
                }
            )
    return deltas

def compare(pre_path: str, post_path: str, as_json: bool) -> int:
    try:
        pre = json.loads(Path(pre_path).read_text(encoding="utf-8"))
        post = json.loads(Path(post_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"worktree-state-fingerprint: cannot read snapshot: {error}", file=sys.stderr)
        return 2

    deltas = _collect_deltas(pre, post)
    if as_json:
        print(json.dumps({"identical": not deltas, "deltas": deltas}, indent=2))
    elif not deltas:
        print("worktree-state-fingerprint: IDENTICAL (all fields)")
    else:
        print(f"worktree-state-fingerprint: {len(deltas)} delta(s):")
        for delta in deltas:
            if delta["field"] == "porcelain":
                print("  porcelain:")
                for line in difflib.unified_diff(
                    str(delta["pre"]).splitlines(),
                    str(delta["post"]).splitlines(),
                    lineterm="",
                    n=1,
                ):
                    print(f"    {line}")
            else:
                print(f"  {delta['field']}: {delta['pre']} -> {delta['post']}")
    return 1 if deltas else 0

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture / compare a byte-level Git worktree state fingerprint."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    cap = sub.add_parser("capture", help="Write a fingerprint snapshot JSON.")
    cap.add_argument("--repo", required=True, help="Path to the git worktree.")
    cap.add_argument("--out", required=True, help="Snapshot JSON output path.")

    cmp_ = sub.add_parser("compare", help="Report deltas between two snapshots.")
    cmp_.add_argument("--pre", required=True, help="Pre snapshot JSON.")
    cmp_.add_argument("--post", required=True, help="Post snapshot JSON.")
    cmp_.add_argument("--json", action="store_true", help="Machine-readable delta report.")

    args = parser.parse_args()
    try:
        if args.command == "capture":
            return capture(args.repo, args.out)
        return compare(args.pre, args.post, args.json)
    except RuntimeError as error:
        print(f"worktree-state-fingerprint: {error}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
