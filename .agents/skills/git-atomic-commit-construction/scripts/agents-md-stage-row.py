#!/usr/bin/env python3
"""
agents-md-stage-row.py — Alphabetically insert a single row into the root
AGENTS.md skills table, then either stage-only-the-row (atomic-commit mode)
or write to the working tree (skill-factory registration mode).

Modes (--mode):
---------------
    staged    (default — original behavior)
        Source: git show HEAD:AGENTS.md
        Sink:   git hash-object -w  +  git update-index --cacheinfo
        Use when: AGENTS.md already has other pending hunks in the
        working tree and you need to commit ONLY the new row alongside
        the related artifact commit (§2f Interleaving Mandate of the
        Atomic Commit Construction workflow). All other working-tree
        edits to AGENTS.md remain untouched.

    worktree  (new — skill-factory registration)
        Source: working-tree AGENTS.md
        Sink:   plain file write (no staging)
        Use when: AGENTS.md is clean (no other pending hunks) and you
        simply want the registration row to appear in the working tree
        for ordinary `git status` review and a normal `git add`. This is
        the standard path during skill-factory new-skill registration
        per skill-factory/SKILL.md §2.3.

Both modes share the same alphabetical insertion algorithm and the same
table-row detection heuristic — only the read source and write sink
differ.

Usage
-----
Dry-run (preview position, no changes either way):
    python3 agents-md-stage-row.py --row "| My Skill | ..." --dry-run

Atomic-commit interleaving (stage HEAD + one row, ignore working tree):
    python3 agents-md-stage-row.py --row "| My Skill | ..."
    python3 agents-md-stage-row.py --mode staged --row "| My Skill | ..."

Skill-factory registration (modify working tree, stage later by hand):
    python3 agents-md-stage-row.py --mode worktree --row "| My Skill | ..."

With explicit repo path (any mode):
    python3 agents-md-stage-row.py --row "..." --repo /path/to/repo
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def git(*args, repo: str) -> str:
    """Run a git command rooted at *repo* and return stripped stdout."""
    result = subprocess.run(
        ["git", "-C", repo, *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def find_repo_root(start: str) -> str:
    """Walk up from *start* until .git is found; raise if not found."""
    path = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(path, ".git")):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            raise RuntimeError("Not inside a git repository.")
        path = parent


def row_sort_key(line: str) -> str | None:
    """
    Return the lowercase sort key for a Markdown table data row,
    or None if the line is a header / separator / non-table line.
    """
    parts = line.split("|")
    if len(parts) < 2:
        return None
    name = parts[1].strip()
    if not name or name in {"Skill", ":---"} or name.startswith(":"):
        return None
    return name.lower()


def insert_row_alphabetically(lines: list[str], new_row: str) -> tuple[list[str], int]:
    """
    Insert *new_row* at the alphabetically correct position in the skills table.
    Returns (new_lines, insertion_index).
    """
    new_key = row_sort_key(new_row)
    if new_key is None:
        raise ValueError(f"Could not extract sort key from row: {new_row!r}")

    result = list(lines)
    for i, line in enumerate(result):
        key = row_sort_key(line)
        if key is not None and key > new_key:
            result.insert(i, new_row)
            return result, i

    # Append after last table row
    for i in range(len(result) - 1, -1, -1):
        if row_sort_key(result[i]) is not None:
            result.insert(i + 1, new_row)
            return result, i + 1

    result.append(new_row)
    return result, len(result) - 1


# ---------------------------------------------------------------------------
# Mode implementations
# ---------------------------------------------------------------------------

def read_head(repo: str) -> list[str]:
    try:
        head_content = git("show", "HEAD:AGENTS.md", repo=repo)
    except subprocess.CalledProcessError as exc:
        sys.exit(f"ERROR: Could not read HEAD:AGENTS.md — {exc.stderr.strip()}")
    return [line + "\n" for line in head_content.splitlines()]


def read_worktree(repo: str) -> list[str]:
    path = Path(repo) / "AGENTS.md"
    if not path.is_file():
        sys.exit(f"ERROR: Working-tree file not found: {path}")
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def sink_staged(repo: str, new_lines: list[str]) -> str:
    """Write a new blob and point the index at it; working tree untouched."""
    content = "".join(new_lines)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tf:
        tf.write(content)
        tmp_path = tf.name
    try:
        blob_hash = git("hash-object", "-w", tmp_path, repo=repo)
        git("update-index", "--cacheinfo", f"100644,{blob_hash},AGENTS.md", repo=repo)
    except subprocess.CalledProcessError as exc:
        sys.exit(f"ERROR: git operation failed — {exc.stderr.strip()}")
    finally:
        os.unlink(tmp_path)
    return blob_hash


def sink_worktree(repo: str, new_lines: list[str]) -> None:
    """Plain file write to AGENTS.md in the working tree."""
    path = Path(repo) / "AGENTS.md"
    path.write_text("".join(new_lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Insert a row into the root AGENTS.md skills table either "
                    "directly into the working tree (--mode worktree, for "
                    "skill-factory registration) or staged-only against HEAD "
                    "(--mode staged, the default — for the §2f Interleaving "
                    "Mandate of the Atomic Commit Construction workflow)."
    )
    parser.add_argument(
        "--row",
        required=True,
        help="Full Markdown table row to insert, e.g. '| Skill Name | path | description |'",
    )
    parser.add_argument(
        "--mode",
        choices=("staged", "worktree"),
        default="staged",
        help="staged (default): read HEAD blob, stage HEAD+row, leave working tree alone. "
             "worktree: read working tree, write working tree, do not touch the index.",
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="Path to the git repository root. Defaults to the repo containing this script.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the insertion position without changing anything.",
    )
    args = parser.parse_args()

    repo = args.repo or find_repo_root(os.path.dirname(os.path.abspath(__file__)))

    new_row = args.row if args.row.endswith("\n") else args.row + "\n"

    if args.mode == "staged":
        source_lines = read_head(repo)
        source_label = "HEAD:AGENTS.md"
    else:
        source_lines = read_worktree(repo)
        source_label = "<worktree>/AGENTS.md"

    try:
        new_lines, idx = insert_row_alphabetically(source_lines, new_row)
    except ValueError as exc:
        sys.exit(f"ERROR: {exc}")

    prev_key = row_sort_key(new_lines[idx - 1]) if idx > 0 else None
    next_key = row_sort_key(new_lines[idx + 1]) if idx + 1 < len(new_lines) else None
    row_key = row_sort_key(new_row)
    print(f"Mode: {args.mode}  (source: {source_label})")
    print(f"Position: insert at line {idx + 1}")
    print(f"  prev row: '{prev_key}'")
    print(f"  new  row: '{row_key}'")
    print(f"  next row: '{next_key}'")

    if args.dry_run:
        print("\n[dry-run] No changes made.")
        return

    if args.mode == "staged":
        blob_hash = sink_staged(repo, new_lines)
        print(f"\nStaged: AGENTS.md (blob {blob_hash})")
        print("Only the new row has been added to the index; all other "
              "working-tree changes remain unstaged.")
    else:
        sink_worktree(repo, new_lines)
        print(f"\nWrote: {Path(repo) / 'AGENTS.md'}")
        print("Working tree updated. Stage normally with: git add AGENTS.md")


if __name__ == "__main__":
    main()
