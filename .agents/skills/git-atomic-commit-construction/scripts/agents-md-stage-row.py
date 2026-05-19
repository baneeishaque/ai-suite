#!/usr/bin/env python3
"""
agents-md-stage-row.py — Alphabetically insert and precisely stage a single
row into the root AGENTS.md skills table without disturbing any other pending
changes in the working tree.

Used during §2f (Interleaving Mandate) of the Atomic Commit Construction
workflow: when AGENTS.md contains mixed hunks (session rows + out-of-scope
rows), this script stages only the session row alongside the artifact commit —
no git add -p gymnastics required.

Mechanism
---------
1. Reads the CURRENT HEAD version of AGENTS.md (not the working tree).
2. Inserts --row at the alphabetically correct position in the skills table.
3. Writes the result as a new blob via `git hash-object -w`.
4. Updates the index directly via `git update-index --cacheinfo`.

Result: AGENTS.md is staged with exactly HEAD + one new row. All other
working-tree changes to AGENTS.md remain unstaged.

Usage
-----
Dry-run (preview position only, no staging):
    python3 agents-md-stage-row.py --row "| My Skill | ..." --dry-run

Stage the row (run from anywhere inside the repo):
    python3 agents-md-stage-row.py --row "| My Skill | ..."

With explicit repo path:
    python3 agents-md-stage-row.py --row "| My Skill | ..." --repo /path/to/repo
"""

import argparse
import os
import subprocess
import sys
import tempfile


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
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Insert a row into HEAD AGENTS.md and stage the result "
                    "without touching other working-tree changes."
    )
    parser.add_argument(
        "--row",
        required=True,
        help="Full Markdown table row to insert, e.g. '| Skill Name | path | description |'",
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="Path to the git repository root. Defaults to the repo containing this script.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the insertion position without staging anything.",
    )
    args = parser.parse_args()

    # Resolve repo root
    repo = args.repo or find_repo_root(os.path.dirname(os.path.abspath(__file__)))

    # Ensure the row ends with a newline
    new_row = args.row if args.row.endswith("\n") else args.row + "\n"

    # Read HEAD version of AGENTS.md
    try:
        head_content = git("show", "HEAD:AGENTS.md", repo=repo)
    except subprocess.CalledProcessError as exc:
        sys.exit(f"ERROR: Could not read HEAD:AGENTS.md — {exc.stderr.strip()}")

    head_lines = [line + "\n" for line in head_content.splitlines()]

    # Compute insertion
    try:
        new_lines, idx = insert_row_alphabetically(head_lines, new_row)
    except ValueError as exc:
        sys.exit(f"ERROR: {exc}")

    # Report position
    prev_key = row_sort_key(new_lines[idx - 1]) if idx > 0 else None
    next_key = row_sort_key(new_lines[idx + 1]) if idx + 1 < len(new_lines) else None
    row_key = row_sort_key(new_row)
    print(f"Position: insert at line {idx + 1}")
    print(f"  prev row: '{prev_key}'")
    print(f"  new  row: '{row_key}'")
    print(f"  next row: '{next_key}'")

    if args.dry_run:
        print("\n[dry-run] No changes staged.")
        return

    # Write blob and update index
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

    print(f"\nStaged: AGENTS.md (blob {blob_hash})")
    print("Only the new row has been added to the index; all other working-tree changes remain unstaged.")


if __name__ == "__main__":
    main()
