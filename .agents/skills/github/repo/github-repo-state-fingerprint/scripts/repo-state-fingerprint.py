#!/usr/bin/env python3
"""repo-state-fingerprint.py — capture/compare GitHub repo state fingerprints.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib; no pip dependencies.

Captures a curated state fingerprint per repository (identity + structure
fields) and compares fingerprints field-by-field:

    compared by default : visibility, default_branch, head_sha, archived, fork
    recorded, ignored   : size, stargazers_count, forks_count,
                          open_issues_count, watchers_count, captured_at
    never compared      : full_name (differs trivially across owners)

`compare` re-captures live state when no `--current` snapshot is supplied, and
`--owner` overrides the owner for live re-capture — enabling cross-owner
comparisons such as verifying a repository transfer.

Usage:
    python3 repo-state-fingerprint.py capture --owner <login> --repos a,b --output baseline.json
    python3 repo-state-fingerprint.py compare --baseline baseline.json --owner <other-owner>

Exit codes:
    0  capture: all captured · compare: all repositories match
    1  capture: any missing/error · compare: any drift/missing/error
    2  usage / configuration error
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import NoReturn

STDERR_STATUS_RE = re.compile(r"\(HTTP (\d{3})\)")
NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")

REPO_JQ = (
    "{full_name: .full_name, visibility: .visibility, "
    "default_branch: .default_branch, archived: .archived, fork: .fork, "
    "size: .size, stargazers_count: .stargazers_count, "
    "forks_count: .forks_count, open_issues_count: .open_issues_count, "
    "watchers_count: .watchers_count}"
)

DEFAULT_COMPARE_KEYS = ["visibility", "default_branch", "head_sha", "archived", "fork"]
ALWAYS_EXCLUDED = {"captured_at", "full_name", "status", "repo", "detail"}
VOLATILE_KEYS = {"size", "stargazers_count", "forks_count",
                 "open_issues_count", "watchers_count"}


def die(msg: str, code: int = 2) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def gh(args: list[str], token: str | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
    try:
        return subprocess.run(
            ["gh", *args], capture_output=True, text=True, encoding="utf-8",
            env=env, timeout=60,
        )
    except OSError as exc:
        die(f"cannot run gh: {exc}")
    except subprocess.TimeoutExpired:
        die("gh call timed out after 60s")


def resolve_token(login: str) -> str:
    try:
        proc = subprocess.run(
            ["gh", "auth", "token", "--user", login],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        die(f"cannot resolve token for {login!r}: {exc}")
    token = proc.stdout.strip()
    if proc.returncode != 0 or not token:
        die(f"no stored gh token for user {login!r} (try: gh auth login)")
    return token


def fetch_repo(owner: str, name: str, token: str | None) -> tuple[dict, int | None]:
    proc = gh(["api", f"repos/{owner}/{name}", "--jq", REPO_JQ], token)
    if proc.returncode == 0:
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return {"status": "error", "detail": "unparseable repo JSON"}, None
        data["status"] = "captured"
        return data, 200
    match = STDERR_STATUS_RE.search(proc.stderr)
    code = int(match.group(1)) if match else None
    if code == 404:
        return {"status": "missing"}, 404
    return {"status": "error", "detail": proc.stderr.strip()[:200]}, code


def fetch_head_sha(owner: str, name: str, token: str | None) -> str:
    proc = gh(["api", f"repos/{owner}/{name}/commits?per_page=1",
               "--jq", '.[0].sha // ""'], token)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def capture_record(owner: str, name: str, token: str | None) -> dict:
    data, _ = fetch_repo(owner, name, token)
    if data.get("status") != "captured":
        return {"repo": name, "status": data.get("status", "error")}
    data["repo"] = name
    data["head_sha"] = fetch_head_sha(owner, name, token)
    data["captured_at"] = utc_now()
    return data


def load_candidates(args: argparse.Namespace) -> list[str]:
    names: list[str] = []
    if args.repos:
        names.extend(part.strip() for part in args.repos.split(","))
    if args.repos_file:
        try:
            with open(args.repos_file, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        names.append(line)
        except OSError as exc:
            die(f"cannot read --repos-file: {exc}")
    seen: set[str] = set()
    unique: list[str] = []
    for name in names:
        if name and name not in seen:
            seen.add(name)
            unique.append(name)
    if not unique:
        die("no candidate names (use --repos and/or --repos-file)")
    for name in unique:
        if not NAME_RE.match(name):
            die(f"invalid repo name: {name!r}")
    return unique


def load_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        die(f"cannot read {path}: {exc}")


def compare_record(baseline: dict, current: dict, strict: bool) -> tuple[str, dict]:
    if baseline.get("status") != "captured":
        return "error", {"baseline_status": baseline.get("status")}
    if current.get("status") == "missing":
        return "missing", {}
    if current.get("status") != "captured":
        return "error", {"current_status": current.get("status"),
                         "detail": current.get("detail", "")}
    if strict:
        keys = sorted(set(baseline) | set(current))
        keys = [k for k in keys if k not in ALWAYS_EXCLUDED]
    else:
        keys = DEFAULT_COMPARE_KEYS
    changes: dict = {}
    for key in keys:
        before, after = baseline.get(key), current.get(key)
        if before != after:
            changes[key] = {"baseline": before, "current": after}
    return ("drift" if changes else "ok"), changes


def main_capture(args: argparse.Namespace) -> int:
    token = resolve_token(args.token_user) if args.token_user else None
    candidates = load_candidates(args)

    records: dict[str, dict] = {}
    exit_code = 0
    for name in candidates:
        record = capture_record(args.owner, name, token)
        records[name] = record
        print(json.dumps(record), flush=True)
        if record.get("status") != "captured":
            exit_code = 1

    snapshot = {"owner": args.owner, "captured_at": utc_now(), "repos": records}
    try:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(snapshot, fh, indent=2)
            fh.write("\n")
    except OSError as exc:
        die(f"cannot write --output: {exc}")
    print(json.dumps({"snapshot": args.output, "owner": args.owner,
                      "repos": len(records), "captured": sum(
                          1 for r in records.values()
                          if r.get("status") == "captured")}), flush=True)
    return exit_code


def main_compare(args: argparse.Namespace) -> int:
    baseline = load_json(args.baseline)
    owner = args.owner or baseline.get("owner")
    if not owner:
        die("no owner: pass --owner or use a baseline that records one")
    baseline_repos = baseline.get("repos") or {}
    if not baseline_repos:
        die("baseline contains no repos")

    token = resolve_token(args.token_user) if args.token_user else None
    current_repos = None
    if args.current:
        current_repos = (load_json(args.current).get("repos") or {})

    counts = {"ok": 0, "drift": 0, "missing": 0, "error": 0}
    for name, baseline_record in baseline_repos.items():
        if current_repos is not None:
            current_record = current_repos.get(name, {"status": "missing"})
        else:
            current_record = capture_record(owner, name, token)
        verdict, changes = compare_record(baseline_record, current_record, args.strict)
        counts[verdict] += 1
        print(json.dumps({"repo": name, "verdict": verdict, "changes": changes}),
              flush=True)

    print(json.dumps({"owner": owner, "baseline": args.baseline,
                      "checked": len(baseline_repos), "counts": counts}), flush=True)
    return 0 if counts["ok"] == len(baseline_repos) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Repo state fingerprint.")
    sub = parser.add_subparsers(dest="mode", required=True)

    cap = sub.add_parser("capture", help="capture a state snapshot")
    cap.add_argument("--owner", required=True, help="owner login")
    cap.add_argument("--repos", help="comma-separated repo names")
    cap.add_argument("--repos-file", help="file with one repo name per line")
    cap.add_argument("--output", required=True, help="snapshot file to write")
    cap.add_argument("--token-user", help="gh-authenticated login whose token to use")

    cmp_ = sub.add_parser("compare", help="compare against a snapshot")
    cmp_.add_argument("--baseline", required=True, help="snapshot to compare against")
    cmp_.add_argument("--current", help="stored snapshot instead of live re-capture")
    cmp_.add_argument("--owner", help="owner override for live re-capture")
    cmp_.add_argument("--token-user", help="gh-authenticated login whose token to use")
    cmp_.add_argument("--strict", action="store_true",
                      help="also compare volatile metrics")

    args = parser.parse_args()
    if args.mode == "capture":
        return main_capture(args)
    return main_compare(args)


if __name__ == "__main__":
    sys.exit(main())
