#!/usr/bin/env python3
"""replace-and-replay.py — deterministic in-place replacement of a single Git commit.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §3 —
subprocess-orchestrated, pure-stdlib; no pip dependencies.

Three-bug avoidance: the replay uses no sequence editor, no rebase-todo
writer, and no interactive stop — `git rebase --autostash --onto <new>
<target> <branch>` is a deterministic one-shot replay (contrast the
interactive `git rebase -i` routes that require a todo writer).

Subcommands:
  prepare --repo <path> --target <sha> [--branch <name>] [--allow-main-worktree] --state-out <state.json>
  finish  --state <state.json> [--message <msg>] [--author "<name <email>>"]
  verify  --state <state.json>

Exit codes:
  0  ok (verify: PARITY_OK)
  2  usage / git error / state mismatch
  3  finish: replay conflict — resolve, `git add`, `git rebase --continue`, then run verify
  4  verify: REVIEW_NEEDED (range-diff shape outside the accepted parity shapes)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_RD_LINE_RE = re.compile(
    r"^(\d+|-+):\s+([0-9a-f]+|-+)\s+([=!<>])\s+(\d+|-+):\s+([0-9a-f]+|-+)"
)

def _run(repo: str, *args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["GIT_PAGER"] = "cat"
    env["GIT_EDITOR"] = "true"
    return subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, text=True, env=env
    )

def _git(repo: str, *args: str, check: bool = True) -> str:
    proc = _run(repo, *args)
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return proc.stdout.strip()

def _load_state(state_path: str) -> dict:
    try:
        return json.loads(Path(state_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"cannot read state file: {error}")

def _save_state(state_path: str, state: dict) -> None:
    Path(state_path).write_text(
        json.dumps(state, indent=2) + "\n", encoding="utf-8"
    )

def prepare(
    repo: str,
    target: str,
    branch: str | None,
    allow_main: bool,
    state_out: str,
) -> int:
    repo_abs = os.path.abspath(repo)
    if not os.path.isdir(repo_abs):
        print(f"replace-and-replay: repo not found: {repo_abs}", file=sys.stderr)
        return 2

    git_dir = os.path.realpath(
        os.path.join(repo_abs, _git(repo_abs, "rev-parse", "--git-dir"))
    )
    common_dir = os.path.realpath(
        os.path.join(repo_abs, _git(repo_abs, "rev-parse", "--git-common-dir"))
    )
    if git_dir == common_dir and not allow_main:
        print(
            "replace-and-replay: refusing to prepare in the MAIN worktree — "
            "use a dedicated linked worktree (or composer Mode A), or pass "
            "--allow-main-worktree explicitly.",
            file=sys.stderr,
        )
        return 2

    target_sha = _git(repo_abs, "rev-parse", "--verify", f"{target}^{{commit}}")
    if branch is None:
        branch = _git(repo_abs, "symbolic-ref", "--short", "-q", "HEAD", check=False)
    if not branch:
        print(
            "replace-and-replay: detached HEAD and no --branch given",
            file=sys.stderr,
        )
        return 2
    pre_tip = _git(repo_abs, "rev-parse", "--verify", f"{branch}^{{commit}}")
    if _run(repo_abs, "merge-base", "--is-ancestor", target_sha, pre_tip).returncode != 0:
        print(
            f"replace-and-replay: target {target_sha[:12]} is not an ancestor "
            f"of {branch} ({pre_tip[:12]})",
            file=sys.stderr,
        )
        return 2

    _git(repo_abs, "checkout", "--detach", target_sha)
    state = {
        "schema_version": 1,
        "repo": repo_abs,
        "worktree": _git(repo_abs, "rev-parse", "--show-toplevel"),
        "target_sha": target_sha,
        "branch": branch,
        "pre_tip": pre_tip,
        "prepared_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_state(state_out, state)
    print(
        f"replace-and-replay: prepared detached HEAD at {target_sha[:12]} "
        f"(branch {branch}, pre_tip {pre_tip[:12]}) -> {state_out}"
    )
    print(
        "replace-and-replay: edit the worktree, stage the change, then run "
        f"finish --state {state_out}"
    )
    return 0

def finish(state_path: str, message: str | None, author: str | None) -> int:
    state = _load_state(state_path)
    repo = state["repo"]
    target = state["target_sha"]
    branch = state["branch"]

    head = _git(repo, "rev-parse", "HEAD")
    if head != target:
        print(
            f"replace-and-replay: HEAD ({head[:12]}) is not the prepared "
            f"target ({target[:12]}) — re-run prepare",
            file=sys.stderr,
        )
        return 2

    has_staged = _run(repo, "diff", "--cached", "--quiet").returncode != 0
    if not has_staged and not message and not author:
        print(
            "replace-and-replay: nothing staged and no --message/--author — "
            "nothing to amend",
            file=sys.stderr,
        )
        return 2

    amend_args = ["commit", "--amend"]
    if author:
        amend_args += ["--author", author]
    if message:
        amend_args += ["-m", message]
    else:
        amend_args += ["--no-edit"]
    _git(repo, *amend_args)
    new_sha = _git(repo, "rev-parse", "HEAD")

    proc = _run(
        repo,
        "-c",
        "rebase.autoSquash=false",
        "-c",
        "rebase.rebaseMerges=false",
        "rebase",
        "--autostash",
        "--onto",
        new_sha,
        target,
        branch,
    )
    if proc.returncode != 0:
        git_dir = _git(repo, "rev-parse", "--git-dir")
        in_rebase = any(
            os.path.isdir(os.path.join(repo, git_dir, name))
            for name in ("rebase-merge", "rebase-apply")
        )
        if in_rebase:
            print(
                "replace-and-replay: replay CONFLICT — resolve the conflicts, "
                "stage the result (`git add <paths>`), run "
                "`GIT_EDITOR=true git rebase --continue`, then run "
                f"verify --state {state_path}. Post-conflict replays are "
                "expected to report REVIEW_NEEDED (resolutions alter "
                "descendant patches) — review the range-diff interdiff.",
                file=sys.stderr,
            )
            return 3
        raise RuntimeError(f"git rebase failed: {proc.stderr.strip()}")

    state["new_sha"] = new_sha
    state["new_tip"] = _git(repo, "rev-parse", f"{branch}^{{commit}}")
    _save_state(state_path, state)
    print(
        f"replace-and-replay: {target[:12]} replaced by {new_sha[:12]}; "
        f"branch {branch} replayed to {state['new_tip'][:12]}"
    )
    return verify(state_path)

def verify(state_path: str) -> int:
    state = _load_state(state_path)
    repo = state["repo"]
    target = state["target_sha"]
    pre_tip = state["pre_tip"]
    branch = state["branch"]
    new_tip = _git(repo, "rev-parse", f"{branch}^{{commit}}")

    if _run(repo, "rev-parse", "--verify", "--quiet", f"{target}^").returncode != 0:
        print("replace-and-replay: verify")
        print(f"  branch: {branch}  new_tip: {new_tip[:12]}")
        print(
            "  verdict: REVIEW_NEEDED — target is a root commit; the "
            "range-diff base <target>^ does not exist — review manually"
        )
        return 4

    rd = _git(
        repo,
        "-c",
        "color.ui=never",
        "range-diff",
        f"{target}^..{pre_tip}",
        f"{target}^..{new_tip}",
    )
    markers = [match.group(3) for line in rd.splitlines() if (match := _RD_LINE_RE.match(line))]
    eqs = markers.count("=")
    bangs = markers.count("!")
    lt = markers.count("<")
    gt = markers.count(">")
    total = int(_git(repo, "rev-list", "--count", f"{target}^..{pre_tip}"))

    changed = bangs + lt
    accounted = eqs + bangs + lt == total and lt == gt
    parity_ok = accounted and changed <= 1
    print("replace-and-replay: verify")
    print(f"  branch: {branch}  new_tip: {new_tip[:12]}")
    print(
        f"  range-diff: {total} old-side commit(s) — "
        f"eqs={eqs} bang={bangs} lt={lt} gt={gt} changed={changed}"
    )
    print(f"  rev-list --count {branch}: {_git(repo, 'rev-list', '--count', branch)}")
    stat = _git(repo, "diff", "--stat", pre_tip, branch)
    print(f"  diff --stat {pre_tip[:12]} {branch}:")
    print(stat if stat else "  (no tree difference)")
    if parity_ok:
        print("  verdict: PARITY_OK")
        return 0
    print("  verdict: REVIEW_NEEDED — raw range-diff follows")
    print(rd)
    return 4

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic in-place replacement of a single Git commit."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    prep = sub.add_parser("prepare", help="Detach at the target commit.")
    prep.add_argument("--repo", required=True, help="Path to the git worktree.")
    prep.add_argument("--target", required=True, help="Commit to replace.")
    prep.add_argument("--branch", default=None, help="Branch to replay (default: current).")
    prep.add_argument(
        "--allow-main-worktree",
        action="store_true",
        help="Permit running in the main worktree (not recommended).",
    )
    prep.add_argument("--state-out", required=True, help="State JSON output path.")

    fin = sub.add_parser("finish", help="Amend the target and replay the branch.")
    fin.add_argument("--state", required=True, help="State JSON from prepare.")
    fin.add_argument("--message", default=None, help="New commit message (reword).")
    fin.add_argument("--author", default=None, help='New author "Name <email>".')

    ver = sub.add_parser("verify", help="Range-diff parity verification.")
    ver.add_argument("--state", required=True, help="State JSON from prepare.")

    args = parser.parse_args()
    try:
        if args.command == "prepare":
            return prepare(
                args.repo, args.target, args.branch, args.allow_main_worktree, args.state_out
            )
        if args.command == "finish":
            return finish(args.state, args.message, args.author)
        return verify(args.state)
    except RuntimeError as error:
        print(f"replace-and-replay: {error}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
