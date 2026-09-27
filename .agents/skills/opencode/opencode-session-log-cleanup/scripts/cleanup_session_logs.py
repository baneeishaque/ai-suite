#!/usr/bin/env python3
"""cleanup_session_logs.py — OpenCode session-log cleanup composer.

Tier 1 (Python 3.12+, stdlib only).
Discovers logger-plugin artifacts for a session ID, verifies with the user,
delegates removal to the safe-file-cleanup base skill, and re-verifies.
"""

import argparse
import os
import subprocess
import sys


def find_session_logs(session_id, logs_dir):
    """Return existing log files/directories for the given session ID."""
    base = os.path.join(logs_dir, session_id)
    paths = []

    for ext in ("state.json", "turns.jsonl", "jsonl"):
        p = f"{base}.{ext}"
        if os.path.exists(p):
            paths.append(p)

    if os.path.isdir(base):
        paths.append(base)

    return paths


def verify_with_user(paths):
    """Print paths and return True if the user confirms."""
    print("The following opencode session log files/directories will be removed:")
    for p in paths:
        print(f"  - {p}")
    print()
    answer = input("Proceed with removal? [y/N] ").strip().lower()
    return answer == "y"


def call_base_cleanup(paths, remove_empty_parents=False):
    """Delegate to safe-file-cleanup and stream its output."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_script = os.path.normpath(
        os.path.join(
            script_dir,
            "..",
            "..",
            "..",
            "general",
            "file",
            "safe-file-cleanup",
            "scripts",
            "safe_cleanup.py",
        )
    )

    if not os.path.exists(base_script):
        print(
            f"ERROR: base skill script not found at {base_script}",
            file=sys.stderr,
        )
        sys.exit(2)

    cmd = ["python3", base_script] + paths
    if remove_empty_parents:
        cmd.append("--remove-empty-parents")

    proc = subprocess.run(cmd, text=True)
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    return proc.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Discover and remove opencode session logs by session ID."
    )
    parser.add_argument("session_id", help="Session ID (e.g. ses_00d820a27ffe...)")
    parser.add_argument(
        "--logs-dir",
        default=".opencode/logs",
        help="Logs directory (default: .opencode/logs)",
    )
    parser.add_argument(
        "--remove-empty-parents",
        action="store_true",
        help="Remove empty parent directories after cleanup",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip user confirmation (use with caution)",
    )
    args = parser.parse_args()

    paths = find_session_logs(args.session_id, args.logs_dir)
    if not paths:
        print(
            f"No log files found for session {args.session_id}",
            file=sys.stderr,
        )
        sys.exit(1)

    if not args.yes:
        if not verify_with_user(paths):
            print("Aborted by user.")
            sys.exit(0)

    rc = call_base_cleanup(paths, args.remove_empty_parents)

    remaining = find_session_logs(args.session_id, args.logs_dir)
    if remaining:
        print(
            f"WARNING: {len(remaining)} path(s) still remain after cleanup:",
            file=sys.stderr,
        )
        for p in remaining:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)

    print(f"Session {args.session_id} logs cleaned up successfully.")
    sys.exit(rc)


if __name__ == "__main__":
    main()
