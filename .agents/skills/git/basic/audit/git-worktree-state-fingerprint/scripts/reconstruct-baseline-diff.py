#!/usr/bin/env python3
"""reconstruct-baseline-diff.py — Replay base-ref + pre-state patch and diff named files.

Rebuilds the pre-state a commit was layered on by checking out ``--base-ref`` in
an isolated worktree, applying ``--pre-state-patch``, then diffing each
``--files`` path against the live worktree. Deltas are reported as IDENTICAL,
DIFFERS, MISSING_IN_BASELINE, or MISSING_IN_LIVE. A delta listed in
``--expected-delta`` is expected; every other delta is unexpected and makes the
script exit 1.

Usage:
    python3 reconstruct-baseline-diff.py --repo <repo> --base-ref <ref> \\
        --pre-state-patch <patch> --files <path> [--files <path> ...] \\
        [--expected-delta <path> ...] [--json]

Exit codes: 0 = no unexpected deltas, 1 = unexpected deltas, 2 = error.
"""

from __future__ import annotations

import argparse
import difflib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and optionally raise on failure."""
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(f"{' '.join(cmd)} failed ({proc.returncode}): {detail}")
    return proc


def compare_file(live: Path, baseline: Path, rel: str) -> dict:
    """Compare one live file against its reconstructed baseline."""
    live_exists = live.is_file()
    baseline_exists = baseline.is_file()
    if not live_exists and not baseline_exists:
        return {"path": rel, "status": "IDENTICAL", "diff": ""}
    if baseline_exists and not live_exists:
        return {"path": rel, "status": "MISSING_IN_LIVE", "diff": ""}
    if live_exists and not baseline_exists:
        return {"path": rel, "status": "MISSING_IN_BASELINE", "diff": ""}
    live_bytes = live.read_bytes()
    baseline_bytes = baseline.read_bytes()
    if live_bytes == baseline_bytes:
        return {"path": rel, "status": "IDENTICAL", "diff": ""}
    live_text = live_bytes.decode("utf-8", errors="replace").splitlines(keepends=True)
    baseline_text = baseline_bytes.decode("utf-8", errors="replace").splitlines(
        keepends=True
    )
    diff = "".join(
        difflib.unified_diff(
            baseline_text,
            live_text,
            fromfile=f"baseline/{rel}",
            tofile=f"live/{rel}",
        )
    )
    return {"path": rel, "status": "DIFFERS", "diff": diff}


def emit_text(records: list[dict], summary: dict) -> None:
    """Print a human-readable report."""
    for record in records:
        marker = " (expected)" if record["expected"] else ""
        print(f"{record['status']:<20} {record['path']}{marker}")
        if record["diff"]:
            print(record["diff"], end="" if record["diff"].endswith("\n") else "\n")
    print(
        f"Summary: {summary['identical']} identical, {summary['differing']} differing, "
        f"{summary['expected']} expected, {summary['unexpected']} unexpected"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replay base-ref + pre-state patch and diff named files."
    )
    parser.add_argument("--repo", default=".", help="Repository root (default: cwd)")
    parser.add_argument("--base-ref", required=True, help="Base commit the commit was layered on")
    parser.add_argument("--pre-state-patch", required=True, help="Saved pre-state patch")
    parser.add_argument(
        "--files",
        action="append",
        required=True,
        metavar="path",
        help="Repo-relative file to verify (repeatable)",
    )
    parser.add_argument(
        "--expected-delta",
        action="append",
        default=[],
        metavar="path",
        help="File whose delta is expected (repeatable)",
    )
    parser.add_argument(
        "--workdir",
        help="Parent directory for the isolated worktree (default: <repo>/scratch)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument(
        "--keep-worktree", action="store_true", help="Keep the reconstructed worktree"
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    patch = Path(args.pre_state_patch).resolve()
    if not patch.is_file():
        print(f"ERROR: patch not found: {patch}", file=sys.stderr)
        sys.exit(2)
    workdir_parent = (
        Path(args.workdir).resolve() if args.workdir else repo / "scratch"
    )
    workdir_parent.mkdir(parents=True, exist_ok=True)
    expected = set(args.expected_delta)

    base = Path(tempfile.mkdtemp(prefix="baseline-reconstruct-", dir=workdir_parent))
    worktree = base / "wt"
    try:
        run(
            [
                "git",
                "-c",
                "core.hooksPath=/dev/null",
                "worktree",
                "add",
                "--detach",
                "--quiet",
                str(worktree),
                args.base_ref,
            ],
            repo,
        )
        run(["git", "apply", "--check", str(patch)], worktree)
        run(["git", "apply", str(patch)], worktree)

        records: list[dict] = []
        for rel in args.files:
            record = compare_file(repo / rel, worktree / rel, rel)
            record["expected"] = rel in expected
            records.append(record)
    except (RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    finally:
        if not args.keep_worktree:
            run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                repo,
                check=False,
            )
            shutil.rmtree(base, ignore_errors=True)
            run(["git", "worktree", "prune"], repo, check=False)

    unexpected = [
        record["path"]
        for record in records
        if record["status"] != "IDENTICAL" and not record["expected"]
    ]
    summary = {
        "identical": sum(1 for record in records if record["status"] == "IDENTICAL"),
        "differing": sum(1 for record in records if record["status"] != "IDENTICAL"),
        "expected": sum(
            1 for record in records if record["expected"] and record["status"] != "IDENTICAL"
        ),
        "unexpected": len(unexpected),
    }

    if args.json:
        print(
            json.dumps(
                {
                    "repo": str(repo),
                    "base_ref": args.base_ref,
                    "pre_state_patch": str(patch),
                    "files": records,
                    "summary": summary,
                    "unexpected": unexpected,
                },
                indent=2,
            )
        )
    else:
        emit_text(records, summary)
    if args.keep_worktree:
        print(f"Worktree kept at: {worktree}", file=sys.stderr)
    sys.exit(1 if unexpected else 0)


if __name__ == "__main__":
    main()
