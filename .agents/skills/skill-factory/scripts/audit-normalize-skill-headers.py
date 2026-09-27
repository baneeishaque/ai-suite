#!/usr/bin/env python3
"""audit-normalize-skill-headers.py — library-wide audit of skill header blockquotes.

Owns the skill-documentation half of the metadata-header convention: discovers
every Author-style skill doc in the library (``**/SKILL.md`` plus the handful of
``**/AGENTS.md`` files that carry the same ``> **Label:**`` header block), runs
the canonical base primitive (``markdown-generation/scripts/join-blockquote-header.py``)
``--check`` on each, and reports/repairs any blockquote header run that renders
collapsed.

DELIBERATE SHELL-OUT (no inlining)
  All header detection and rewriting is delegated to the base
  ``join-blockquote-header.py`` (self-anchored relative to this file, never
  ``sys.path``-dependent). This file only: discovers candidates, filters cheaply,
  shells ``--check`` / ``--apply``, aggregates the per-file verdicts, and maps
  them to exit codes. The base script is the single source of truth for both the
  transform and the header-line regex — duplication is a violation.

CONTRACT
  Invocation   : scripts/audit-normalize-skill-headers.py [--apply]
                 [--files <glob>] [--root <path>]
  default      : --check mode; prints one verdict line per candidate
  Exit 0       : every candidate clean
  Exit 1       : non-conformant candidate(s) found (or --apply rewrote and the
                 post-apply sweep still finds residue)
  --check      : report-only, no writes (same as default)
  --apply      : run the base script --apply on each non-conformant file
  --files      : restrict discovery to paths matching this fnmatch glob
                 (relative to the skills root; e.g. ``--files '**/markdown-generation/**'``)
  --root       : override the repo root auto-discovery
  --verbose    : print a one-line summary for every candidate (default prints
                 only non-conformant + summary)

EXIT CODE USAGE
  Safe to wire into pre-commit / CI: exit 1 aborts when any skill doc header
  block needs normalization.
"""
from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys
from pathlib import Path

BASE_REL = Path("markdown-generation/scripts/join-blockquote-header.py")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
DOC_PATTERNS = ("**/SKILL.md", "**/AGENTS.md")


def find_repo_root(start: Path) -> Path:
    p = start.resolve()
    for ancestor in (p, *p.parents):
        if (ancestor / "AGENTS.md").is_file() and (ancestor / ".agents" / "skills").is_dir():
            return ancestor
    sys.exit(f"FATAL: could not find repo root (AGENTS.md + .agents/skills/) above {start}")


def base_script_path(start: Path) -> Path:
    repo_root = find_repo_root(start)
    return repo_root / ".agents" / "skills" / BASE_REL


def discover_docs(skills_root: Path, files_glob: str | None) -> list[Path]:
    docs: list[Path] = []
    for pattern in DOC_PATTERNS:
        for p in skills_root.glob(pattern):
            if not p.is_file():
                continue
            rel = p.relative_to(skills_root)
            if any(part in SKIP_DIRS for part in rel.parts):
                continue
            if files_glob and not fnmatch.fnmatch(str(rel), files_glob):
                continue
            docs.append(p)
    return sorted(set(docs))


def is_candidate(text: str) -> bool:
    """Cheap pre-filter: the header block marks the top of the file, so a ``> **``
    blockquote token anywhere is a strong signal worth paying for a real check."""
    return "> **" in text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report only, exit 1 when fixes are needed (default)")
    ap.add_argument("--apply", action="store_true", help="run the base --apply on non-conformant files")
    ap.add_argument("--files", default=None, help="fnmatch glob scoping candidates relative to the skills root")
    ap.add_argument("--root", default=None, help="repository root (auto-discovered)")
    ap.add_argument("--version", action="store_true", help="print the base script to use and exit")
    args = ap.parse_args()

    script = base_script_path(Path(__file__).resolve())
    if not script.is_file():
        sys.exit(f"FATAL: base script missing: {script}")

    root = Path(args.root).resolve() if args.root else find_repo_root(Path(__file__).resolve())
    skills_root = root / ".agents" / "skills"
    docs = discover_docs(skills_root, args.files)

    if args.version:
        print(script)
        return 0

    mode = "apply" if args.apply else "check"
    nonconformant: list[Path] = []
    checked = 0
    for doc in docs:
        try:
            text = doc.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not is_candidate(text):
            continue
        checked += 1
        probe = subprocess.run(
            [sys.executable, str(script), "--check", str(doc)],
            capture_output=True,
            text=True,
        )
        if probe.returncode == 0:
            continue
        nonconformant.append(doc)

    if mode == "apply" and nonconformant:
        failures: list[Path] = []
        for doc in nonconformant:
            fix = subprocess.run(
                [sys.executable, str(script), "--apply", str(doc)],
                capture_output=True,
                text=True,
            )
            print(f"[audit-normalize] applied: {doc.relative_to(root)}")
            probe = subprocess.run(
                [sys.executable, str(script), "--check", str(doc)],
                capture_output=True,
                text=True,
            )
            if probe.returncode != 0:
                failures.append(doc)
        for doc in failures:
            print(f"[audit-normalize] FAILED: {doc.relative_to(root)}", file=sys.stderr)
        nonconformant = failures

    for doc in nonconformant:
        print(f"[audit-normalize] needs normalization: {doc.relative_to(root)}")

    print(
        f"[audit-normalize] {mode.upper()} — {checked} candidates checked, "
        f"{len(nonconformant)} non-conformant"
    )
    return 1 if nonconformant else 0


if __name__ == "__main__":
    raise SystemExit(main())