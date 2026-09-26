#!/usr/bin/env python3
"""Pre-commit dangling markdown link detector (git-aware).

Walks a root tree, finds every NON-gitignored *.md file, extracts markdown
link targets, resolves each relative target, and classifies it:

- EXISTS   — target exists on disk
- GIT_ONLY — absent on disk but present in the git index
- DANGLES  — absent from BOTH working tree and index (blocking audit)
- IGNORED  — exists on disk but is gitignored (delegated out, not counted)

Output: one JSON record per finding (JSONL) unless --json (array):
{"file": str, "target": str, "resolved": str, "class": str, "note": str}

Exit codes: 0 = no DANGLES, 1 = at least one DANGLES, 2 = usage error.

Usage:
  detect-dangling-links.py [--root <dir>] [--json] [--output <file>]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

SKIP_PREFIXES = ("http://", "https://", "file://", "#", "mailto:", "tel:", "data:")
LINK_RE = re.compile(r"\]\(([^()\s]+)\)")


def git(args: list[str], cwd: Path, stdin_text: str | None = None) -> tuple[int, str]:
    try:
        r = subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True, text=True, timeout=60,
            input=stdin_text,
            stdin=subprocess.DEVNULL if stdin_text is None else None,
        )
        return r.returncode, r.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return -1, ""


def repo_root(cwd: Path) -> Path | None:
    rc, out = git(["rev-parse", "--show-toplevel"], cwd)
    if rc != 0:
        return None
    return Path(out.strip())


def ignored_set(root: Path, md_files: list[Path]) -> set[Path]:
    """Set of gitignored md paths under root (via `git check-ignore --stdin`)."""
    if not md_files:
        return set()
    payload = "\n".join(str(p) for p in md_files) + "\n"
    rc, out = git(["check-ignore", "--stdin"], root, stdin_text=payload)
    if rc not in (0, 1):
        return set()
    return {Path(x) for x in out.splitlines()}


def walk_md(root: Path) -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        dirnames[:] = [d for d in dirnames if not (Path(dirpath) / d / ".git").exists()]
        for f in filenames:
            if f.endswith(".md"):
                found.append(Path(dirpath) / f)
    return found


def extract_targets(text: str) -> list[str]:
    """Extract markdown link targets, skipping fenced code and inline code."""
    targets: list[str] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r"`[^`]*`", "", line)
        for m in LINK_RE.finditer(line):
            raw = m.group(1).strip()
            target = raw.split(" ", 1)[0]
            target = target.rsplit('"', 1)[0]
            target = target.rsplit("'", 1)[0]
            if any(target.startswith(p) for p in SKIP_PREFIXES):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            if "." not in target and "/" not in target:
                # bare prose like [text](scope) — not a path-shaped target
                continue
            targets.append(target)
    return targets


def tracked_set(root: Path) -> set[Path]:
    """One-shot `git ls-files` -> set of index-paths (relative to root)."""
    rc, out = git(["ls-files", "-z"], root)
    if rc != 0:
        return set()
    return {Path(x) for x in out.split("\0") if x}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="pre-commit dangling markdown link detector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--root", default=".", help="directory to scan (default .)")
    ap.add_argument("--json", action="store_true",
                    help="emit one JSON array instead of JSONL")
    ap.add_argument("--output", help="write to file instead of stdout")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: --root not a directory: {root}", file=sys.stderr)
        return 2

    rr = repo_root(root)
    if rr is None:
        print("WARN: no git repo at root; GIT_ONLY classification unavailable",
              file=sys.stderr)
        rr = root

    ignored = ignored_set(root, walk_md(root))
    tracked = tracked_set(root) if rr is not None else set()
    findings: list[dict] = []

    for md in walk_md(root):
        rel_md = md.relative_to(rr) if str(md).startswith(str(rr)) else md
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for target in extract_targets(text):
            unquoted = urllib.parse.unquote(target)
            resolved = (md.parent / unquoted).resolve()
            cls: str
            note = ""
            if resolved.is_dir() or resolved.is_file():
                cls = "IGNORED" if resolved in ignored else "EXISTS"
                if cls == "IGNORED":
                    note = "exists on disk but gitignored — delegated out"
            elif rr is not None and str(resolved).startswith(str(rr)):
                rel = resolved.relative_to(rr)
                if rel in tracked:
                    cls = "GIT_ONLY"
                    note = "absent on disk but present in the git index"
                else:
                    cls = "DANGLES"
                    note = "absent from working tree AND index"
            else:
                cls = "DANGLES"
                note = "resolved outside repo; absent on disk"
            findings.append({
                "file": str(rel_md),
                "target": target,
                "resolved": str(resolved),
                "class": cls,
                "note": note,
            })

    danglers = [f for f in findings if f["class"] == "DANGLES"]
    for d in danglers:
        print(f"[DANGLES] {d['file']} -> {d['target']} ({d['note']})",
              file=sys.stderr)

    if args.json:
        text = json.dumps(findings, ensure_ascii=False, indent=2)
    else:
        text = "".join(json.dumps(f, ensure_ascii=False) + "\n" for f in findings)
    if args.output:
        Path(args.output).write_text(text)
    else:
        sys.stdout.write(text)
    return 1 if danglers else 0


if __name__ == "__main__":
    raise SystemExit(main())