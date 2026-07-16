#!/usr/bin/env python3
"""Audit a submodule's URL state and history.

Tier: 1 (Python 3.12+).
Cite: scripting-language-selection-rules.md §2 (Tier-1 default).
Rationale for Python (vs Tier-2 pwsh / bash): the audit fans out multiple
`git` subprocess calls and aggregates them into a single structured report
(state / urls / history) consumed by the composer. Per §2.4 inverse this
is NOT a ≤80% shell-glue case — Python wins on argparse, structured output,
and clean exit-code semantics. Per skill-factory §3.1 Plan-Time Tier
Declaration.

Composed by: git-submodule-misconfiguration-audit-and-revert/SKILL.md Phase 2.
"""

from __future__ import annotations

import argparse
import configparser
import subprocess
import sys
from pathlib import Path


def git(repo: Path, *args: str, check: bool = False,
        cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd or repo), *args],
        capture_output=True, text=True, encoding="utf-8", check=check,
    )


def gitmodules_url(repo: Path, name: str) -> str | None:
    res = git(repo, "config", "-f", ".gitmodules",
              f"submodule.{name}.url", check=False)
    return res.stdout.strip() or None


def submodule_name_for_path(repo: Path, path: str) -> str | None:
    """Resolve submodule.<NAME>.path == <path>."""
    cfg_path = repo / ".gitmodules"
    if not cfg_path.exists():
        return None
    parser = configparser.ConfigParser()
    parser.read_string(cfg_path.read_text(encoding="utf-8"))
    for section in parser.sections():
        if not section.startswith("submodule "):
            continue
        if parser.get(section, "path", fallback=None) == path:
            return section.split('"')[1]
    return None


def live_origin(repo: Path, sub_path: str) -> str | None:
    sub_repo = repo / sub_path
    res = git(repo, "remote", "get-url", "origin",
              cwd=sub_repo, check=False)
    return res.stdout.strip() or None


def is_detached(repo: Path, sub_path: str) -> bool:
    sub_repo = repo / sub_path
    res = git(repo, "symbolic-ref", "-q", "HEAD",
              cwd=sub_repo, check=False)
    return res.returncode != 0


def ahead_behind(repo: Path, sub_path: str,
                 ref: str = "origin/HEAD") -> tuple[int, int] | None:
    sub_repo = repo / sub_path
    res = git(repo, "rev-list", "--left-right", "--count",
              f"HEAD...{ref}", cwd=sub_repo, check=False)
    if res.returncode != 0:
        return None
    parts = res.stdout.split()
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


def default_branch(repo: Path, sub_path: str) -> str:
    sub_repo = repo / sub_path
    res = git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD",
              cwd=sub_repo, check=False)
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip()
    return "origin/HEAD"


def url_history(repo: Path, url_fragments: list[str]) -> list[str]:
    """Find commits touching .gitmodules for any of the given URL fragments."""
    seen: dict[str, str] = {}
    for frag in url_fragments:
        if not frag:
            continue
        res = git(repo, "log", "--all", "--format=%H %ad %an %s",
                  "--date=short", "-S", frag, "--", ".gitmodules",
                  check=False)
        for line in res.stdout.splitlines():
            sha = line.split(" ", 1)[0]
            seen.setdefault(sha, line)
    return list(seen.values())


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", required=True, type=Path)
    p.add_argument("--submodule", required=True,
                   help="Submodule path (e.g., vendor/foo)")
    p.add_argument("--expected-url", default=None,
                   help="Optional: expected canonical URL (for mismatch flag)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    repo: Path = args.repo.resolve()
    sub_path: str = args.submodule

    name = submodule_name_for_path(repo, sub_path)
    if name is None:
        sys.stderr.write(
            f"submodule path not found in .gitmodules: {sub_path}\n")
        return 2

    declared = gitmodules_url(repo, name)
    live = live_origin(repo, sub_path)
    detached = is_detached(repo, sub_path)
    default_ref = default_branch(repo, sub_path)
    counts = ahead_behind(repo, sub_path, default_ref)

    # URL-fragment basis: owner segment of each known URL.
    fragments: list[str] = []
    for u in (declared, live, args.expected_url):
        if u and "/" in u:
            tail = u.rstrip("/").split("/")[-2:]
            fragments.append("/".join(tail))
    history = url_history(repo, fragments)

    print("== STATE ==")
    print(f"submodule_name: {name}")
    print(f"submodule_path: {sub_path}")
    print(f"detached_head:  {str(detached).lower()}")
    if counts is None:
        print("ahead/behind:   <unavailable>")
    else:
        ahead, behind = counts
        print(f"ahead:          {ahead}")
        print(f"behind:         {behind}  (vs {default_ref})")
    print()
    print("== URLS ==")
    print(f".gitmodules:    {declared or '<missing>'}")
    print(f"live origin:    {live or '<missing>'}")
    mismatch = bool(declared and live and declared != live)
    print(f"mismatch:       {str(mismatch).lower()}")
    if args.expected_url:
        exp_ok = (declared == args.expected_url and
                  live == args.expected_url)
        print(f"expected_url:   {args.expected_url}")
        print(f"matches_expect: {str(exp_ok).lower()}")
    print()
    print("== HISTORY ==")
    print("URL-touching commits on .gitmodules (newest-first):")
    if not history:
        print("  <none>")
    else:
        for line in history:
            print(f"  {line}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
