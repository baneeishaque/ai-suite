#!/usr/bin/env python3
"""verify-commit-preview.py — Verify commit-preview execution status against git history.

Parses a commit-preview markdown file (the §2d format produced by the
git-atomic-commit-construction composer) and cross-references each
listed "Commit N:" section title against `git log --oneline` to report
which arranged commits have been executed and which remain pending.

Read-only by default; optional --cleanup delegates to safe-file-cleanup
only when every listed commit is found. The caller must first verify
content, outstanding actions, references, and explicit retirement consent.
On macOS, missing Trash fails closed. No permanent-removal code lives here.

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §§3–5:
portable parsing and subprocess composition, with no ecosystem-specific runtime.

Usage
-----
    python3 verify-commit-preview.py --preview <path> [--repo <path>] [--format text|json] [--cleanup]

    python3 verify-commit-preview.py --preview scratch/commit-preview.md
    python3 verify-commit-preview.py --preview scratch/commit-preview.md --format json
    python3 verify-commit-preview.py --preview scratch/commit-preview.md --cleanup

Exit Codes
----------
    0   All commits verified as executed
    1   One or more commits not found in git log
    2   Preview file not found or unreadable
    3   Not inside a git repository (and --repo not provided)
    4   Preview file contains no parseable commit entries
    5   Cleanup unavailable, failed, or unverified
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

COMMIT_HEADER_RE = re.compile(r"^#{1,6}\s*Commit\s+(\d+)\s*:\s*(.+?)\s*$", re.MULTILINE)
CLEANUP_SCRIPT = (
    Path(__file__).resolve().parents[5]
    / "general/file/safe-file-cleanup/scripts/safe_cleanup.py"
)


def cleanup_preview(preview_path: Path) -> dict[str, object]:
    """Delegate one authorized retirement; require a verified removal result."""
    if not CLEANUP_SCRIPT.is_file():
        raise RuntimeError(f"cleanup helper not found: {CLEANUP_SCRIPT}")
    if sys.platform == "darwin" and shutil.which("trash") is None:
        raise RuntimeError("macOS Trash is unavailable; preview retained")
    result = subprocess.run(
        [sys.executable, str(CLEANUP_SCRIPT), str(preview_path.absolute()), "--json"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"cleanup helper exited {result.returncode}: {detail}")
    try:
        record = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("cleanup helper returned invalid JSON") from error
    if not isinstance(record, dict) or record.get("status") != "removed":
        raise RuntimeError("cleanup helper did not confirm removal")
    if os.path.lexists(preview_path):
        raise RuntimeError("cleanup helper reported removal but preview still exists")
    return record


def find_repo_root(start: str) -> str:
    """Walk up from *start* until .git is found; raise if not found."""
    path = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(path, ".git")):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            raise RuntimeError("Not inside a git repository.")
        path = parent


def run_git_log(repo: str, window: int = 50) -> list[str]:
    """Return git log --oneline lines (newest first) for the given repo."""
    env = dict(os.environ)
    env["GIT_PAGER"] = "cat"
    result = subprocess.run(
        ["git", "-C", repo, "log", "--oneline", f"-{window}"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.splitlines()


def parse_commits(text: str) -> list[dict[str, object]]:
    """Extract ordered Commit N entries from a preview markdown body."""
    entries: list[dict[str, object]] = []
    for index_str, title in COMMIT_HEADER_RE.findall(text):
        entries.append({"index": int(index_str), "title": title.strip()})
    return entries


def find_sha(log_lines: list[str], title: str) -> str | None:
    """Return the full log line (sha + title) whose tail matches *title*, else None."""
    target = title.strip()
    for line in log_lines:
        # git log --oneline lines are "<sha> <subject>"
        if " " in line:
            _, subject = line.split(" ", 1)
        else:
            subject = line
        if subject.strip() == target:
            return line.split(" ", 1)[0]
        if target in line:
            return line.split(" ", 1)[0]
    return None


def format_text(report: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append("Commit Preview Verification")
    lines.append("=" * 26)
    lines.append(f"Preview: {report['preview_file']}")
    lines.append(f"Repository: {report['repo']}")
    lines.append("")
    header = f"{'#':>2}  {'Status':<7}  {'SHA':<8}  Title"
    lines.append(header)
    for commit in report["commits"]:  # type: ignore[union-attr]
        index = commit["index"]
        status = commit["status"]
        sha = commit["sha"] or ""
        title = commit["title"]
        mark = "done" if status == "done" else "PENDING"
        lines.append(f"{index:>2}  {mark:<7}  {sha:<8}  {title}")
    lines.append("")
    lines.append(
        f"Result: {report['done']}/{report['total']} commits executed"
    )
    if report["pending"]:
        lines.append(
            "WARNING: pending commits found — preview must be retained for the next session."
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify whether commits listed in a commit-preview "
        "markdown file have been executed against git history."
    )
    parser.add_argument(
        "--preview",
        required=True,
        help="Path to the commit-preview markdown file (e.g. scratch/commit-preview.md).",
    )
    parser.add_argument(
        "--repo",
        default="",
        help="Git repository root. Defaults to auto-detection from CWD.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=50,
        help="git log window size in commits (default: 50).",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Retire a verified preview via safe-file-cleanup; requires prior caller consent and coverage checks.",
    )
    args = parser.parse_args()

    preview_path = Path(args.preview)
    if not preview_path.is_file() or not os.access(preview_path, os.R_OK):
        print(f"ERROR: preview file not found or unreadable: {preview_path}", file=sys.stderr)
        return 2

    try:
        repo = os.path.abspath(args.repo) if args.repo else find_repo_root(os.getcwd())
    except RuntimeError:
        print(
            "ERROR: not inside a git repository (use --repo to specify one).",
            file=sys.stderr,
        )
        return 3

    if not os.path.isdir(os.path.join(repo, ".git")):
        print(
            f"ERROR: {repo} is not a git repository (no .git directory).",
            file=sys.stderr,
        )
        return 3

    text = preview_path.read_text(encoding="utf-8")
    commits = parse_commits(text)
    if not commits:
        print(
            "ERROR: no parseable 'Commit N:' entries found in preview file.",
            file=sys.stderr,
        )
        return 4

    log_lines = run_git_log(repo, window=args.window)

    for commit in commits:
        sha = find_sha(log_lines, str(commit["title"]))  # type: ignore[arg-type]
        commit["status"] = "done" if sha else "pending"
        commit["sha"] = sha

    done = sum(1 for c in commits if c["status"] == "done")
    pending = len(commits) - done

    report: dict[str, object] = {
        "preview_file": args.preview,
        "repo": repo,
        "total": len(commits),
        "done": done,
        "pending": pending,
        "commits": commits,
    }

    exit_code = 0 if pending == 0 else 1
    if args.cleanup:
        if pending:
            report["cleanup"] = {"status": "refused", "reason": "pending commits"}
            print(
                "Cleanup refused: pending commits present — preview retained.",
                file=sys.stderr,
            )
        else:
            try:
                report["cleanup"] = cleanup_preview(preview_path)
            except (OSError, subprocess.SubprocessError, RuntimeError) as error:
                report["cleanup"] = {"status": "failed", "reason": str(error)}
                print(f"Cleanup failed: {error}", file=sys.stderr)
                exit_code = 5

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(format_text(report))
        if args.cleanup and exit_code == 0:
            print(f"Cleaned up: {args.preview}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
