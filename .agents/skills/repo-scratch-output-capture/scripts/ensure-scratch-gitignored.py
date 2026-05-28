#!/usr/bin/env python3
"""
ensure-scratch-gitignored.py
============================

Idempotently create ``<repo-root>/scratch/`` and add ``scratch/`` to
``.gitignore``. Emits the absolute path to ``scratch/`` on stdout
(suitable for command substitution).

Usage
-----
    SCRATCH="$(python3 path/to/ensure-scratch-gitignored.py)"

Exit codes
----------
0  scratch directory ready (created or pre-existing) and .gitignore patched
1  not inside a git repository

Tier
----
Tier-1 (Python) per ``scripting-language-selection-rules.md`` — pure
stdlib filesystem + line-membership work. Ported from
``ensure-scratch-gitignored.sh`` per ``script-language-tier-port``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def git_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(
            "[ensure-scratch-gitignored] ERROR: not inside a git repository",
            file=sys.stderr,
        )
        sys.exit(1)
    return Path(result.stdout.strip())


def ensure_line(gitignore: Path, line: str) -> None:
    if gitignore.is_file():
        existing = gitignore.read_text().splitlines()
        if line in existing:
            return
        sep = "" if gitignore.read_text().endswith("\n") else "\n"
        with gitignore.open("a") as fh:
            fh.write(f"{sep}{line}\n")
    else:
        gitignore.write_text(f"{line}\n")


def main() -> int:
    repo = git_repo_root()
    scratch = repo / "scratch"
    scratch.mkdir(exist_ok=True)
    ensure_line(repo / ".gitignore", "scratch/")
    print(scratch)
    return 0


if __name__ == "__main__":
    sys.exit(main())
