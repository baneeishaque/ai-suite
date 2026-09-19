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


def mask_code(text: str) -> str:
    """Blank fenced blocks + inline code, preserving offsets and newlines."""
    def blank(m: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))
    masked = FENCED_RE.sub(blank, text)
    return INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), masked)


def collect_links(text: str, masked: str) -> List[Tuple[int, int, str, str, str]]:
    """Return (start, end, label, target, kind) for ../ links outside code."""
    out: List[Tuple[int, int, str, str, str]] = []
    for m in INLINE_LINK_RE.finditer(masked):
        s, e = m.span()
        orig = INLINE_LINK_RE.match(text, s, e)
        label = orig.group(1) if orig else m.group(1)
        out.append((s, e, label, m.group(2), "inline"))
    for m in REF_DEF_RE.finditer(masked):
        s, e = m.span(1)
        out.append((s, e, "(ref-def)", m.group(1), "ref-def"))
    return sorted(out)


def line_no(text: str, offset: int) -> int:
    """1-based line number for offset."""
    return text.count("\n", 0, offset) + 1


def nearest_existing(dirpath: Path) -> Path:
    """Nearest existing ancestor (for git probing of not-yet-created targets)."""
    cur = dirpath
    while not cur.exists() and cur != cur.parent:
        cur = cur.parent
    return cur


def suggest_parent_url(resolved: Path) -> Optional[str]:
    """Build a SHA-pinned GitHub URL if the target sits in a GitHub repo."""
    anchor = nearest_existing(resolved.parent if resolved.suffix else resolved)
    outer = find_root_git(anchor)
    if outer is None:
        return None
    try:
        rel = resolved.relative_to(outer)
    except ValueError:
        return None
    _, remote = run_git(["config", "--get", "remote.origin.url"], outer)
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", remote or "")
    if not m:
        return None
    _, sha = run_git(["rev-parse", "HEAD"], outer)
    if not re.fullmatch(r"[0-9a-f]{40}", sha or ""):
        return None
    return f"https://github.com/{m.group(1)}/{m.group(2)}/blob/{sha}/{rel.as_posix()}"


def audit_file(
    filepath: Path, repo_root: Path, suggest_urls: bool = True
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Audit one markdown file. Returns (findings, warnings)."""
    findings: List[Dict[str, Any]] = []
    warnings: List[str] = []
    try:
        text = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        warnings.append(f"{filepath}: skipped (non-UTF-8)")
        return findings, warnings
    except OSError as exc:
        warnings.append(f"{filepath}: unreadable ({exc})")
        return findings, warnings
    try:
        rel = filepath.resolve().relative_to(repo_root)
        allowed_ups = len(rel.parent.parts)
    except ValueError:
        allowed_ups = 0
    masked = mask_code(text)
    for s, e, label, target, kind in collect_links(text, masked):
        up_count = target.count("../")
        resolved = (filepath.parent / target).resolve()
        try:
            resolved.relative_to(repo_root)
            in_repo = True
        except ValueError:
            in_repo = False
        if in_repo:
            continue
        item: Dict[str, Any] = {
            "file": str(filepath),
            "line": line_no(text, s),
            "label": label,
            "target": target,
            "kind": kind,
            "up_count": up_count,
            "allowed_ups": allowed_ups,
            "resolved": str(resolved),
        }
        if suggest_urls:
            url = suggest_parent_url(resolved)
            if url:
                item["suggested_url"] = url
        findings.append(item)
    return findings, warnings


def iter_md_files(
    inputs: List[Path], include_submodules: bool
) -> Tuple[List[Path], List[str]]:
    """Expand files/dirs to a *.md list. Skips nested repos unless requested."""
    files: List[Path] = []
    warnings: List[str] = []
    for inp in inputs:
        p = Path(inp)
        if not p.exists():
            warnings.append(f"{inp}: path does not exist")
            continue
        if p.is_file():
            if p.suffix == ".md":
                files.append(p.resolve())
            else:
                warnings.append(f"{inp}: not a .md file, skipped")
            continue
        for dirpath, dirnames, filenames in os.walk(p, followlinks=False):
            cur = Path(dirpath)
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            if not include_submodules:
                nested = [d for d in list(dirnames) if (cur / d / ".git").exists()]
                for d in nested:
                    warnings.append(f"{cur / d}: nested repo skipped (use --include-submodules)")
                    dirnames.remove(d)
            for f in filenames:
                if f.endswith(".md"):
                    files.append((cur / f).resolve())
    return sorted(set(files)), warnings


def apply_name_only_fix(filepath: Path, findings: List[Dict[str, Any]]) -> int:
    """Replace findings back-to-front (offset-safe). Returns count applied."""
    text = filepath.read_text(encoding="utf-8")
    masked = mask_code(text)
    spans = [(s, e, label) for s, e, label, _, _ in collect_links(text, masked)]
    targets = {(f["label"], f["target"]) for f in findings if f["file"] == str(filepath)}
    # Keep only spans whose (label, target) pair is a reported finding.
    span_targets = {(s, e): t for s, e, _, t, _ in collect_links(text, masked)}
    todo = sorted(
        [(s, e, label) for s, e, label in spans if (label, span_targets.get((s, e))) in targets],
        reverse=True,
    )
    for s, e, label in todo:
        text = text[:s] + f"`{label}` (in a sibling repository)" + text[e:]
    filepath.write_text(text, encoding="utf-8")
    return len(todo)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point. Exit 0 clean, 1 findings, 2 usage/error."""
    ap = argparse.ArgumentParser(
        description="Flag markdown ../ links escaping their enclosing Git repo."
    )
    ap.add_argument("paths", nargs="+", help="Files or directories to scan")
    ap.add_argument("--root", default=None, help="Force repo root (skip discovery)")
    ap.add_argument("--no-git", action="store_true", help="Skip git discovery (fs fallback)")
    ap.add_argument("--include-submodules", action="store_true")
    ap.add_argument("--no-suggest-urls", action="store_true")
    ap.add_argument("--fix", action="store_true", help="Name-only stub (pedagogical refs only)")
    ap.add_argument("--json", action="store_true", help="Emit JSON array")
    ap.add_argument("--strict", action="store_true", help="Warnings exit 2")
    args = ap.parse_args(argv)

    if args.fix:
        print(
            "NOTE: --fix writes name-only stubs; operational refs need "
            "SHA-pinned hosted URLs instead (redaction-portability §0.2).",
            file=sys.stderr,
        )

    files, warnings = iter_md_files([Path(p) for p in args.paths], args.include_submodules)
    if not files and warnings:
        for w in warnings:
            print(f"WARNING: {w}", file=sys.stderr)
        return 2

    forced_root = Path(args.root).resolve() if args.root else None
    if forced_root is not None and not forced_root.is_dir():
        print(f"ERROR: --root {args.root} is not a directory", file=sys.stderr)
        return 2

    all_findings: List[Dict[str, Any]] = []
    # Group files by discovered root so mixed-repo scans stay correct.
    by_root: Dict[str, List[Tuple[Path, str]]] = {}
    for f in files:
        if forced_root is not None:
            root, method = forced_root, "forced"
        else:
            root, method = find_repo_root(f, use_git=not args.no_git)
        if root is None:
            warnings.append(f"{f}: no repo root found ({method}); skipped")
            continue
        by_root.setdefault(str(root), []).append((f, method))

    for root_s, group in sorted(by_root.items()):
        root = Path(root_s)
        for f, method in group:
            f_find, f_warn = audit_file(f, root, suggest_urls=not args.no_suggest_urls)
            for item in f_find:
                item["repo_root"] = str(root)
                item["repo_method"] = method
            all_findings.extend(f_find)
            warnings.extend(f_warn)

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    if args.json:
        print(json.dumps(all_findings, indent=2))
    elif all_findings:
        print(f"Found {len(all_findings)} cross-repo link(s):")
        for d in all_findings:
            sug = f"\n    suggest: {d['suggested_url']}" if d.get("suggested_url") else ""
            print(
                f"  {d['file']}:{d['line']} [{d['label']}]({d['target']})"
                f" — {d['up_count']} up(s), allowed {d['allowed_ups']}"
                f" → {d['resolved']}{sug}"
            )
    else:
        print("OK: no cross-repo links.")

    if args.fix and all_findings:
        per_file: Dict[str, List[Dict[str, Any]]] = {}
        for d in all_findings:
            per_file.setdefault(d["file"], []).append(d)
        for fp, items in per_file.items():
            n = apply_name_only_fix(Path(fp), items)
            print(f"  → {fp}: stubbed {n} link(s)")

    if all_findings:
        return 1
    if warnings and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
