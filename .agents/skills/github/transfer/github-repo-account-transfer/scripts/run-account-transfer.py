#!/usr/bin/env python3
"""run-account-transfer.py — orchestrate a full GitHub repo account transfer.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib. Top-level composer: each
subcommand delegates to one transfer composite script with stdio inherited and
the child's exit code returned.

Stages:
    gate      -> github-repo-transfer-destination-conflict-check
    baseline  -> github-repo-transfer-baseline-capture
    initiate  -> github-repo-transfer-initiate
    wait      -> github-repo-transfer-completion-poll
    verify    -> github-repo-transfer-verify
    cleanup   -> github-repo-collaborator-remove
    repoint   -> git-remote-origin-repoint

Human gate: between `initiate` and `wait`, the destination account must accept
the confirmation email (acceptance is email-based; 1-day expiry).

Usage:
    python3 run-account-transfer.py <stage> [stage flags]

Exit codes:
    the delegated stage's exit code (0 success / 1 stage failure / 2 config)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

STAGE_SCRIPTS = {
    "gate": "github/transfer/github-repo-transfer-destination-conflict-check/scripts/check-destination-conflicts.py",
    "baseline": "github/transfer/github-repo-transfer-baseline-capture/scripts/capture-transfer-baseline.py",
    "initiate": "github/transfer/github-repo-transfer-initiate/scripts/initiate-repo-transfers.py",
    "wait": "github/transfer/github-repo-transfer-completion-poll/scripts/poll-transfer-completion.py",
    "verify": "github/transfer/github-repo-transfer-verify/scripts/verify-repo-transfer.py",
    "cleanup": "github/repo/github-repo-collaborator-remove/scripts/remove-repo-collaborators.py",
    "repoint": "git/repo/git-remote-origin-repoint/scripts/repoint-origin-remotes.py",
}


def die(msg: str, code: int = 2) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def locate_skills_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "skill-factory" / "SKILL.md").is_file():
            return parent
    die("cannot locate .agents/skills root (no skill-factory/SKILL.md marker found)")


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repos", help="comma-separated repo names")
    parser.add_argument("--repos-file", help="file with one repo name per line")
    parser.add_argument("--token-user",
                        help="gh-authenticated login whose token to use")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Account transfer dispatcher.")
    sub = parser.add_subparsers(dest="stage", required=True)

    gate = sub.add_parser("gate", help="destination conflict gate")
    gate.add_argument("--destination-owner", required=True)
    gate.add_argument("--enumerate", action="store_true")
    add_common(gate)

    baseline = sub.add_parser("baseline", help="capture the pre-transfer baseline")
    baseline.add_argument("--old-owner", required=True)
    baseline.add_argument("--output", required=True)
    add_common(baseline)

    initiate = sub.add_parser("initiate", help="initiate the transfers")
    initiate.add_argument("--old-owner", required=True)
    initiate.add_argument("--destination-owner", required=True)
    initiate.add_argument("--execute", action="store_true")
    add_common(initiate)

    wait = sub.add_parser("wait", help="poll for landing at the destination")
    wait.add_argument("--destination-owner", required=True)
    wait.add_argument("--interval", type=int, default=15)
    wait.add_argument("--attempts", type=int, default=20)
    add_common(wait)

    verify = sub.add_parser("verify", help="two-sided fingerprint verification")
    verify.add_argument("--baseline", required=True)
    verify.add_argument("--old-owner", required=True)
    verify.add_argument("--destination-owner", required=True)
    add_common(verify)

    cleanup = sub.add_parser("cleanup", help="remove interim collaborators")
    cleanup.add_argument("--owner", required=True)
    cleanup.add_argument("--collaborator", required=True)
    cleanup.add_argument("--execute", action="store_true")
    add_common(cleanup)

    repoint = sub.add_parser("repoint", help="repoint local clone origins")
    repoint.add_argument("--clones-root", required=True)
    repoint.add_argument("--new-owner", required=True)
    repoint.add_argument("--remote", default="origin")
    repoint.add_argument("--url-template",
                         default="https://github.com/{owner}/{repo}.git")
    repoint.add_argument("--execute", action="store_true")
    add_common(repoint)

    return parser


def add_opt(cmd: list[str], flag: str, value: object | None) -> None:
    if value is not None and value is not False:
        cmd.append(flag)
        if value is not True:
            cmd.append(str(value))


def build_argv(args: argparse.Namespace, script: Path) -> list[str]:
    cmd = [sys.executable, str(script)]
    stage = args.stage

    if stage == "gate":
        cmd += ["--destination-owner", args.destination_owner]
        add_opt(cmd, "--enumerate", args.enumerate)
    elif stage == "baseline":
        cmd += ["--old-owner", args.old_owner, "--output", args.output]
    elif stage == "initiate":
        cmd += ["--old-owner", args.old_owner,
                "--destination-owner", args.destination_owner]
        add_opt(cmd, "--execute", args.execute)
    elif stage == "wait":
        cmd += ["--destination-owner", args.destination_owner,
                "--interval", str(args.interval),
                "--attempts", str(args.attempts)]
    elif stage == "verify":
        cmd += ["--baseline", args.baseline,
                "--old-owner", args.old_owner,
                "--destination-owner", args.destination_owner]
    elif stage == "cleanup":
        cmd += ["--owner", args.owner, "--collaborator", args.collaborator]
        add_opt(cmd, "--execute", args.execute)
    elif stage == "repoint":
        cmd += ["--clones-root", args.clones_root,
                "--new-owner", args.new_owner, "--remote", args.remote,
                "--url-template", args.url_template]
        add_opt(cmd, "--execute", args.execute)

    add_opt(cmd, "--repos", args.repos)
    add_opt(cmd, "--repos-file", args.repos_file)
    add_opt(cmd, "--token-user", args.token_user)
    return cmd


def main() -> int:
    args = build_parser().parse_args()
    root = locate_skills_root()
    script = root / STAGE_SCRIPTS[args.stage]
    if not script.is_file():
        die(f"stage script missing: {script}")

    cmd = build_argv(args, script)
    print(f"[run-account-transfer] stage={args.stage}", file=sys.stderr)
    try:
        proc = subprocess.run(cmd)
    except OSError as exc:
        die(f"cannot run stage: {exc}")
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
