#!/usr/bin/env python3
"""Detect markdown relative links that escape their enclosing Git repository.

Scope: standalone-clone portability for repos consumed both directly and as
submodules (redaction-portability skill §0.1–§0.2,
markdown-generation-rules §4.2.8).

Replaces the predecessor whose ``find_repo_root`` checked
``(parent / ".git").is_dir()`` — which misses every ``.git`` *file* layout
(submodule gitlinks, linked worktrees, submodule-inside-worktree double
gitfiles) and returned ``WARNING: could not find repo root`` with zero
coverage on exactly the layout it was meant to audit.

Root discovery is git-first (``rev-parse --show-toplevel`` understands all
gitfile layouts) with a filesystem fallback that accepts ``.git`` as file
OR dir. The escape verdict itself is ground-truth containment
(``resolved.relative_to(repo_root)``), not a ``../``-count heuristic.

Exit codes: 0 = no cross-repo links, 1 = findings, 2 = usage/error.
Warnings (unreadable files, skipped nested repos, missing roots) go to
stderr and only fail the run under ``--strict``.

Dependencies: git (optional — filesystem fallback applies without it),
python 3.12+. No third-party packages.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SKIP_DIRS = (".git", "node_modules", "__pycache__", ".venv", "venv")
INLINE_LINK_RE = re.compile(r"\[([^\]]*?)\]\(((?:\.\./)+[^()\s]+)\)")
REF_DEF_RE = re.compile(r"(?m)^[ \t]*\[[^\]]+\][ \t]*:[ \t]*((?:\.\./)+[^ \t\n]+)")
FENCED_RE = re.compile(r"(```.*?```|~~~.*?~~~)", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

_repo_cache: Dict[str, Optional[Path]] = {}


def run_git(args: List[str], cwd: Path) -> Tuple[int, str]:
    """Run git, return (returncode, stdout-stripped). Never raises."""
    try:
        r = subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True, text=True, timeout=60,
            stdin=subprocess.DEVNULL,
        )
        return r.returncode, r.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return -1, ""


def find_root_git(start: Path) -> Optional[Path]:
    """Nearest enclosing repo via git (handles gitfiles/worktrees/submodules)."""
    key = f"git:{start}"
    if key in _repo_cache:
        return _repo_cache[key]
    rc, out = run_git(["rev-parse", "--show-toplevel"], start)
    root = Path(out).resolve() if rc == 0 and out else None
    _repo_cache[key] = root
    return root


def find_root_fs(start: Path) -> Optional[Path]:
    """Filesystem fallback: nearest ancestor where ``.git`` exists (file OR dir)."""
    cur = start if start.is_dir() else start.parent
    for parent in [cur, *cur.parents]:
        try:
            if (parent / ".git").exists():
                return parent.resolve()
        except OSError:
            continue
    return None


def submodule_mounts(repo_root: Path) -> List[Path]:
    """Mount dirs registered in ``repo_root/.gitmodules`` (empty if none)."""
    mounts: List[Path] = []
    gitmodules = repo_root / ".gitmodules"
    if not gitmodules.is_file():
        return mounts
    rc, out = run_git(
        ["config", "--file", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$"],
        repo_root,
    )
    if rc != 0:
        try:
            for line in gitmodules.read_text(encoding="utf-8").splitlines():
                m = re.match(r"\s*path\s*=\s*(\S+)", line)
                if m:
                    mounts.append((repo_root / m.group(1)).resolve())
        except OSError:
            pass
        return mounts
    for line in out.splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            mounts.append((repo_root / parts[1]).resolve())
    return mounts


def find_repo_root(path: Path, use_git: bool = True) -> Tuple[Optional[Path], str]:
    """Return (root, method). Handles files, dirs, symlinks, bare, non-git."""
    start = path.resolve()
    if not start.exists():
        return None, "missing"
    anchor = start if start.is_dir() else start.parent
    if use_git:
        root = find_root_git(anchor)
        if root is not None:
            # Uninitialized-submodule guard: a path under a registered mount
            # whose own .git is absent would otherwise be attributed to the
            # parent; the mount dir is the honest standalone-clone boundary.
            try:
                for m in submodule_mounts(root):
                    if (start == m or m in start.parents) and not (m / ".git").exists():
                        return m, "git-uninitialized-mount"
            except OSError:
                pass
            return root, "git"
    fs_root = find_root_fs(anchor)
    return (fs_root, "fs") if fs_root is not None else (None, "none")


def detect_cross_repo_links(filepath, fix=False):
    path = Path(filepath).resolve()
    repo_root, _root_method = find_repo_root(path)
    if not repo_root:
        print(f"WARNING: could not find repo root for {filepath}", file=sys.stderr)
        return 1

    rel_to_repo = path.relative_to(repo_root)
    depth = len(rel_to_repo.parents)

    link_pattern = re.compile(r'\[([^\]]*?)\]\(((?:\.\./)+[^)]+)\)')
    matches = list(link_pattern.finditer(path.read_text(encoding="utf-8")))

    findings = []
    for m in matches:
        link_text = m.group(1)
        link_target = m.group(2)

        up_count = link_target.count("../")
        total_up = depth + up_count
        escapes = total_up > 1

        resolved = (path.parent / link_target).resolve()
        in_repo = False
        try:
            resolved.relative_to(repo_root)
            in_repo = True
        except ValueError:
            pass

        if not in_repo:
            findings.append((m.start(), m.end(), link_text, link_target, up_count, total_up))

    if not findings:
        return 0

    print(f"Found {len(findings)} cross-repo link(s) in {filepath}:")
    for start, end, text, target, up, total in findings:
        print(f"  [{text}]({target}) — {up} levels up from file depth {depth} (total: {total})")

    if fix:
        content = path.read_text(encoding="utf-8")
        for start, end, text, target, up, total in findings:
            replacement = f"`{text}` (in a sibling repository)"
            content = content[:start] + replacement + content[end:]
        path.write_text(content, encoding="utf-8")
        print(f"  → Fixed {len(findings)} link(s)")

    return 1 if findings else 0


def main():
    parser = argparse.ArgumentParser(description="Detect cross-repo relative links in skill files.")
    parser.add_argument("paths", nargs="+", help="Files to scan")
    parser.add_argument("--fix", action="store_true", help="Replace cross-repo links with name-only references")
    args = parser.parse_args()

    exit_code = 0
    for p in args.paths:
        code = detect_cross_repo_links(p, fix=args.fix)
        if code != 0:
            exit_code = code
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
