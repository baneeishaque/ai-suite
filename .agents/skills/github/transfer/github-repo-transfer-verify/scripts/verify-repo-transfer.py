#!/usr/bin/env python3
"""verify-repo-transfer.py — verify a completed repository transfer.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib. Composes the base skill
`github-repo-state-fingerprint` (compare subcommand) twice.

Runs the fingerprint `compare` twice against the pre-transfer baseline:
  1. against the OLD owner  — every repo must be `missing` (gone from the old account)
  2. against the NEW owner  — every repo must be `ok` (identical structure + head SHA)

Usage:
    python3 verify-repo-transfer.py --baseline <snapshot.json> \
        --old-owner <login> --destination-owner <login> [--token-user <login>]

Exit codes:
    0  pass — old owner missing all, destination ok all
    1  fail — any unexpected verdict on either side
    2  usage / configuration error
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

BASE_REL = Path("github/repo/github-repo-state-fingerprint/scripts/repo-state-fingerprint.py")


def die(msg: str, code: int = 2) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def locate_base_script() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "skill-factory" / "SKILL.md").is_file():
            candidate = parent / BASE_REL
            if candidate.is_file():
                return candidate
            die(f"base skill script missing: {candidate}")
    die("cannot locate .agents/skills root (no skill-factory/SKILL.md marker found)")


def run_compare(script: Path, baseline: str, owner: str,
                token_user: str | None) -> tuple[list[dict], dict]:
    cmd = [sys.executable, str(script), "compare",
           "--baseline", baseline, "--owner", owner]
    if token_user:
        cmd += ["--token-user", token_user]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", timeout=600)
    except (OSError, subprocess.TimeoutExpired) as exc:
        die(f"cannot run fingerprint compare: {exc}")
    records: list[dict] = []
    summary: dict | None = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "counts" in obj:
            summary = obj
        else:
            records.append(obj)
    if summary is None:
        die(f"fingerprint compare produced no summary "
            f"(stderr: {proc.stderr.strip()[:200]})")
    return records, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a repo transfer.")
    parser.add_argument("--baseline", required=True, help="pre-transfer snapshot")
    parser.add_argument("--old-owner", required=True, help="source account")
    parser.add_argument("--destination-owner", required=True,
                        help="receiving account")
    parser.add_argument("--token-user",
                        help="gh-authenticated login whose token to use")
    args = parser.parse_args()

    script = locate_base_script()

    records_old, summary_old = run_compare(
        script, args.baseline, args.old_owner, args.token_user)
    print(json.dumps({"stage": "old-owner", "summary": summary_old,
                      "repos": records_old}), flush=True)

    records_new, summary_new = run_compare(
        script, args.baseline, args.destination_owner, args.token_user)
    print(json.dumps({"stage": "destination-owner", "summary": summary_new,
                      "repos": records_new}), flush=True)

    checked = summary_old.get("checked", 0)
    counts_old = summary_old.get("counts", {})
    counts_new = summary_new.get("counts", {})
    old_missing = (
        checked > 0
        and counts_old.get("missing", 0) == checked
        and counts_old.get("ok", 0) == 0
        and counts_old.get("drift", 0) == 0
        and counts_old.get("error", 0) == 0
    )
    new_ok = (
        checked > 0
        and counts_new.get("ok", 0) == checked
        and counts_new.get("drift", 0) == 0
        and counts_new.get("missing", 0) == 0
        and counts_new.get("error", 0) == 0
    )
    verdict = "pass" if old_missing and new_ok else "fail"
    print(json.dumps({"verdict": verdict, "old_missing": old_missing,
                      "new_ok": new_ok, "checked": checked}), flush=True)
    return 0 if verdict == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
