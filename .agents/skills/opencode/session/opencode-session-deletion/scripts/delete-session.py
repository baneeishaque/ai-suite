#!/usr/bin/env python3
"""delete-session.py — delete an OpenCode session end-to-end.

Discovers the database record, logger-plugin artifacts, scratch files, and
(optionally) planning artifacts for a session, prints the inventory, and with
``--execute`` removes them: ``opencode session delete`` for the DB record,
the ``opencode-session-log-cleanup`` script for logs, and
``safe-file-cleanup`` for individual scratch/plan files. Finally re-enumerates
to verify that nothing remains.

Exit codes: 0 success, 1 nothing found / paths remain, 2 fatal.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd=None):
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    return result


def repo_root() -> Path:
    result = run(["git", "rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        sys.exit("FATAL: not inside a Git repository")
    return Path(result.stdout.strip())


def short_id(session_id: str) -> str:
    return session_id[4:] if session_id.startswith("ses_") else session_id


def discover_logs(logs_dir: Path, session_id: str) -> list[Path]:
    found: list[Path] = []
    turn_dir = logs_dir / session_id
    if turn_dir.is_dir():
        found.append(turn_dir)
    for suffix in (".jsonl", ".state.json", ".turns.jsonl"):
        candidate = logs_dir / f"{session_id}{suffix}"
        if candidate.is_file():
            found.append(candidate)
    return found


def discover_scratch(scratch_root: Path, session_id: str) -> list[Path]:
    base = scratch_root / short_id(session_id)
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("*") if p.is_file())


def discover_docs(docs_dir: Path, session_id: str) -> list[Path]:
    if not docs_dir.is_dir():
        return []
    token = short_id(session_id)
    return sorted(p for p in docs_dir.glob(f"*{token}*") if p.is_file())


def db_session_exists(session_id: str) -> bool | None:
    result = run(["opencode", "session", "list"])
    if result.returncode != 0:
        return None
    return session_id in result.stdout


def remove_empty_dirs(path: Path) -> None:
    if not path.is_dir():
        return
    for current, _, _ in sorted(
        ((p, None, None) for p in path.rglob("*") if p.is_dir()),
        key=lambda item: len(item[0].parts),
        reverse=True,
    ):
        try:
            current.rmdir()
        except OSError:
            pass
    try:
        path.rmdir()
    except OSError:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Delete an OpenCode session end-to-end.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("session_id", help="OpenCode session ID (e.g. ses_<id>)")
    parser.add_argument("--logs-dir", default=".opencode/logs", help="Logs directory")
    parser.add_argument("--scratch-root", default="scratch", help="Scratch root")
    parser.add_argument("--docs-dir", default="docs", help="Docs directory")
    parser.add_argument("--dry-run", action="store_true", help="Inventory only (default)")
    parser.add_argument("--execute", action="store_true", help="Perform the deletion")
    parser.add_argument("--retire-docs", action="store_true", help="Also trash matching docs files")
    parser.add_argument("--skip-db", action="store_true", help="Do not call opencode session delete")
    parser.add_argument(
        "--gap-closure-cleared",
        action="store_true",
        help="Acknowledge gap-closure ran and zero gaps remain (required with --execute)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    execute = args.execute and not args.dry_run
    repo = repo_root()
    logs_dir = (repo / args.logs_dir).resolve()
    scratch_root = (repo / args.scratch_root).resolve()
    docs_dir = (repo / args.docs_dir).resolve()

    logs = discover_logs(logs_dir, args.session_id)
    scratch = discover_scratch(scratch_root, args.session_id)
    docs = discover_docs(docs_dir, args.session_id) if args.retire_docs else []
    db_present = db_session_exists(args.session_id)

    inventory = {
        "session_id": args.session_id,
        "db_present": db_present,
        "logs": [str(p) for p in logs],
        "scratch": [str(p) for p in scratch],
        "docs": [str(p) for p in docs],
    }

    if args.json:
        print(json.dumps(inventory, indent=2))
    else:
        print(f"session: {args.session_id}")
        print(f"db record present: {db_present}")
        for label, items in (("logs", logs), ("scratch", scratch), ("docs", docs)):
            print(f"{label}: {len(items)}")
            for item in items:
                print(f"  {item}")

    if not logs and not scratch and not docs and db_present is not True:
        sys.stderr.write("No artifacts found for this session.\n")
        return 1

    if not execute:
        return 0

    if not args.gap_closure_cleared:
        sys.stderr.write(
            "BLOCKED: run skill-library-gap-closure on this session and close all "
            "gaps first, then pass --gap-closure-cleared.\n"
        )
        return 2

    if not args.skip_db and db_present is not False:
        result = run(["opencode", "session", "delete", args.session_id])
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            sys.stderr.write("FATAL: opencode session delete failed.\n")
            return 2

    cleanup = (
        repo
        / ".agents/skills/opencode/opencode-session-log-cleanup/scripts/cleanup_session_logs.py"
    )
    if logs:
        if not cleanup.is_file():
            sys.stderr.write(f"FATAL: missing composed script {cleanup}\n")
            return 2
        result = run(
            [sys.executable, str(cleanup), args.session_id, "--logs-dir", str(logs_dir), "--yes"]
        )
        if result.returncode != 0:
            sys.stderr.write(result.stdout)
            sys.stderr.write(result.stderr)

    safe = repo / ".agents/skills/general/file/safe-file-cleanup/scripts/safe_cleanup.py"
    removable = [str(p) for p in scratch] + [str(p) for p in docs]
    if removable:
        if not safe.is_file():
            sys.stderr.write(f"FATAL: missing composed script {safe}\n")
            return 2
        result = run([sys.executable, str(safe)] + removable)
        if result.returncode != 0:
            sys.stderr.write(result.stdout)
            sys.stderr.write(result.stderr)

    remove_empty_dirs(scratch_root / short_id(args.session_id))

    remaining_logs = discover_logs(logs_dir, args.session_id)
    remaining_scratch = discover_scratch(scratch_root, args.session_id)
    remaining_docs = discover_docs(docs_dir, args.session_id) if args.retire_docs else []
    remaining_db = db_session_exists(args.session_id)

    if remaining_logs or remaining_scratch or remaining_docs or remaining_db is True:
        sys.stderr.write(
            "WARNING: artifacts remain: "
            f"logs={len(remaining_logs)} scratch={len(remaining_scratch)} "
            f"docs={len(remaining_docs)} db={remaining_db}\n"
        )
        return 1

    print("OK: session deleted and verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
