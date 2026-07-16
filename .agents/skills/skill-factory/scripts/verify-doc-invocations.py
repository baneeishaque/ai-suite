#!/usr/bin/env python3
"""verify-doc-invocations.py — owned by skill-factory mandate #7.

Scan all ``**/SKILL.md`` files for fragile tool-invocation patterns embedded
in documentation code blocks.  Exit non-zero when violations are found.

RATIONALE: Skills MUST use simplified invocation forms (``python3``, ``node``,
``ruby``, ``php``, ``pwsh``) in documentation.  Fragile path-resolution
commands (``PY=~/.local/share/mise/installs/python/$(ls ... | sort ...)``,
hard-coded ``/bin/`` paths, etc.) are FORBIDDEN in docs — the script is
responsible for its own tool resolution at runtime.

PATTERNS DETECTED (all case-sensitive):
  - Shell variable assignment that builds a tool path via ``$(ls ... | sort ...)``
  - Literal ``~/.local/share/mise/installs/`` (direct mise-install-path reference)
  - Hard-coded ``/bin/`` tool paths inside fenced bash blocks (exception:
    ``/usr/bin/env``, ``/bin/bash``, ``/bin/sh``, ``/bin/zsh`` — these are
    shebang conventions, not fragile invocation)

CONTRACT:
  Invocation     : scripts/verify-doc-invocations.py
  Exit 0         : no violations found
  Exit 1         : violations found (details printed to stderr)
  --fix          : automatically correct simple patterns where possible
  --scope <glob> : limit scan to matching files (default: ``**/SKILL.md``)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

VIOLATION_PATTERNS: list[tuple[str, re.Pattern]] = [
    (
        "mise-install-path",
        re.compile(r'\$\(ls\s+\S*?(sort|tail).*?\)'),
    ),
    (
        "literal-mise-installs-dir",
        re.compile(r'~\/\.local\/share\/mise\/installs\/'),
    ),
    (
        "export-dynamic-py-path",
        re.compile(r'export\s+PY=.*\$\(ls.*sort.*tail\)'),
    ),
    (
        "hardcoded-bin-path",
        re.compile(
            r'((?<!/usr/bin/env)(?<!/bin/bash)(?<!/bin/sh)(?<!/bin/zsh))'
            r'/bin/(python|node|ruby|php|pwsh|npm|npx|pip)\b'
        ),
    ),
]

FIX_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (
        re.compile(r'export\s+PY=\$HOME/\.local/share/mise/installs/python/\$\(ls.*?\)/bin/python(<error\d*>)'),
        "mise-install-path",
        "python3",
    ),
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def discover_skill_md_files(root: Path, scope_glob: str | None) -> list[Path]:
    pattern = scope_glob or "**/SKILL.md"
    files: list[Path] = []
    for p in root.glob(pattern):
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.is_file():
            files.append(p)
    return sorted(files)


def extract_bash_code_blocks(text: str) -> list[tuple[int, int, str]]:
    blocks: list[tuple[int, int, str]] = []
    lines = text.splitlines(keepends=False)
    in_block = False
    start = 0
    content_lines: list[int] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```") and not in_block:
            in_block = True
            lang = stripped[3:].strip()
            start = i + 1
            content_lines = []
        elif stripped.startswith("```") and in_block:
            if content_lines:
                block_text = "\n".join(lines[start - 1 : i])
                if any(lang in tag for tag in ["bash", "sh", "shell", "zsh", "console"]):
                    blocks.append((start, i, block_text))
            in_block = False
    return blocks


def check_block(block_text: str) -> list[tuple[str, str, int]]:
    violations: list[tuple[str, str, int]] = []
    for name, pattern in VIOLATION_PATTERNS:
        for m in pattern.finditer(block_text):
            line_offset = block_text[: m.start()].count("\n") + 1
            violations.append((name, m.group(), line_offset))
    return violations


def find_repo_root(start: Path) -> Path:
    p = start.resolve()
    for ancestor in (p, *p.parents):
        if (ancestor / "AGENTS.md").is_file() and (ancestor / ".agents" / "skills").is_dir():
            return ancestor
    sys.exit(f"FATAL: could not find repo root (AGENTS.md + .agents/skills/) above {start}")


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scope", default=None, help="Glob for files to scan (default: **/SKILL.md)")
    ap.add_argument("--fix", action="store_true", help="Auto-correct simple patterns")
    args = ap.parse_args()

    root = find_repo_root(Path(__file__).resolve())
    files = discover_skill_md_files(root, args.scope)

    total_violations = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        blocks = extract_bash_code_blocks(text)
        file_violations: list[tuple[str, str, int]] = []
        for start_line, end_line, block_text in blocks:
            for name, match, offset_in_block in check_block(block_text):
                abs_line = start_line + offset_in_block
                file_violations.append((name, match, abs_line))
        if file_violations:
            rel = f.relative_to(root)
            print(f"\n[{rel}]", file=sys.stderr)
            for name, match, line in file_violations:
                snippet = match[:80] + "..." if len(match) > 80 else match
                print(f"  L{line} ({name}): {snippet!r}", file=sys.stderr)
            total_violations += len(file_violations)

    if total_violations == 0:
        print("[verify-doc-invocations] Clean — no fragile invocation patterns found.")
        return 0
    print(f"\n[verify-doc-invocations] {total_violations} violation(s) across {len(files)} file(s).", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
