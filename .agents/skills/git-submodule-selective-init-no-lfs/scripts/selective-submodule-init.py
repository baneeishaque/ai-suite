#!/usr/bin/env python3
"""Selective per-path submodule initialization with a hard No-LFS contract.

Name matches skill `git-submodule-selective-init-no-lfs`: BOTH guarantees
(per-path scope AND no LFS bytes fetched) are enforced and post-verified.

Tier: 1 (Python 3.12+).
Cite: scripting-language-selection-rules.md §2 (Tier-1 default).
Rationale for Python (vs Tier-2 pwsh / bash): post-init verification needs
filesystem walking (`.git/modules/<path>/lfs/objects`) plus structured
parsing of `git submodule status` output — both natural in Python and
brittle in shell. Per skill-factory §3.1 Plan-Time Tier Declaration.

Composed by: git-submodule-selective-init-no-lfs/SKILL.md Phase 1.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None,
        check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, cwd=str(cwd), env=env, check=check,
        capture_output=True, text=True, encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", required=True, type=Path,
                   help="Path to the superproject working tree.")
    p.add_argument("--submodule", required=True, action="append",
                   dest="submodules",
                   help="Submodule path to initialize (repeatable).")
    return p.parse_args()


def selective_init(repo: Path, paths: list[str]) -> None:
    env = os.environ.copy()
    env["GIT_LFS_SKIP_SMUDGE"] = "1"
    cmd = [
        "git", "-C", str(repo),
        "-c", "filter.lfs.smudge=",
        "-c", "filter.lfs.process=",
        "-c", "filter.lfs.required=false",
        "submodule", "update", "--init", "--",
        *paths,
    ]
    res = run(cmd, cwd=repo, env=env, check=False)
    if res.returncode != 0:
        sys.stderr.write(res.stderr)
        sys.exit(res.returncode)


def verify_initialized(repo: Path, sub: str) -> tuple[bool, str]:
    res = run(["git", "-C", str(repo), "submodule", "status", "--", sub],
              cwd=repo, check=False)
    if res.returncode != 0 or not res.stdout:
        return False, f"submodule status failed for {sub}: {res.stderr.strip()}"
    line = res.stdout.splitlines()[0]
    if line.startswith("-"):
        return False, f"{sub} still uninitialized: {line!r}"
    return True, line


def verify_no_lfs(repo: Path, sub: str) -> tuple[bool, str]:
    lfs_dir = repo / ".git" / "modules" / sub / "lfs" / "objects"
    if not lfs_dir.exists():
        return True, "no lfs dir"
    blobs = [p for p in lfs_dir.rglob("*") if p.is_file()]
    if blobs:
        return False, f"{len(blobs)} lfs objects under {lfs_dir}"
    return True, "lfs dir empty"


def main() -> int:
    args = parse_args()
    repo: Path = args.repo.resolve()
    if not (repo / ".git").exists():
        sys.stderr.write(f"not a git repo: {repo}\n")
        return 2

    selective_init(repo, args.submodules)

    failures = 0
    for sub in args.submodules:
        ok_init, msg_init = verify_initialized(repo, sub)
        ok_lfs, msg_lfs = verify_no_lfs(repo, sub)
        status = "OK" if (ok_init and ok_lfs) else "FAIL"
        print(f"[{status}] {sub}")
        print(f"    init: {msg_init}")
        print(f"    lfs:  {msg_lfs}")
        if not (ok_init and ok_lfs):
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
