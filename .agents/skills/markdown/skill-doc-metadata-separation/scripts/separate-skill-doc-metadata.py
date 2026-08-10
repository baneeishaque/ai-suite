#!/usr/bin/env python3
"""Audit and separate skill-doc metadata sections (Changelog / Traceability) into companion files.

Tier 1 (Python) per scripting-language-selection-rules.md Section 3: subprocess orchestration +
argparse + JSON-free aggregation; standard library only. Runs on any Python >= 3.10.

Domain composer for `markdown-section-to-companion-doc` (the base primitive). Owns:

- the domain vocabulary (which sections are metadata: Changelog, Traceability, ...),
- the companion-name mapping (Changelog -> CHANGELOG.md, Traceability -> TRACEABILITY.md),
- the discovery loop (a single skill dir, or a recursive sweep of a library root),
- the batch + re-verify lifecycle: audit -> plan -> split -> re-audit.

All actual file mutation is delegated to the base script; this script never edits markdown itself.

Exit codes:
  0  compliant (check mode: no inline sections; split mode: all planned splits succeeded + re-check clean)
  1  violations found (check mode) / base script missing, base failure, or re-check still dirty (split mode)
  2  usage error
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

BASE_REL = Path("markdown-section-to-companion-doc") / "scripts" / "split-section.py"
DEFAULT_SECTIONS = ["Changelog", "Traceability"]
DEFAULT_POINTERS = {
    "Changelog": "See [CHANGELOG.md](CHANGELOG.md).",
    "Traceability": "See [TRACEABILITY.md](TRACEABILITY.md).",
}
DEFAULT_COMPANION_NAMES = {
    "Changelog": "CHANGELOG.md",
    "Traceability": "TRACEABILITY.md",
}


def base_script() -> Path:
    return Path(__file__).resolve().parent.parent.parent / BASE_REL


def find_skill_docs(target: Path) -> List[Path]:
    """SKILL.md of the target dir itself, or every SKILL.md below a library root."""
    if (target / "SKILL.md").is_file():
        return [target / "SKILL.md"]
    if not target.is_dir():
        raise FileNotFoundError(f"target not found: {target}")
    return sorted(target.rglob("SKILL.md"))


def run_base(base: Path, args: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(base), *args],
        capture_output=True,
        text=True,
    )


def audit(target: Path, sections: List[str]) -> List[Tuple[Path, str]]:
    """Return [(doc, section)] for every inline (violating) metadata section."""
    base = base_script()
    if not base.is_file():
        raise FileNotFoundError(
            f"base script not found: {base} "
            "(is markdown-section-to-companion-doc installed beside this skill?)"
        )
    violations: List[Tuple[Path, str]] = []
    for doc in find_skill_docs(target):
        for section in sections:
            proc = run_base(base, ["--doc", str(doc), "--section", section, "--check"])
            if proc.returncode == 1:
                violations.append((doc, section))
            elif proc.returncode not in (0, 1):
                print(f"separate-skill-doc-metadata: base check failed for {doc} "
                      f"({section}): {proc.stderr.strip()}", file=sys.stderr)
                raise SystemExit(1)
    return violations


def plan_split(doc: Path, section: str, pointer_overrides: Dict[str, str]) -> Tuple[List[str], str]:
    """Invocation args for the base split and the companion filename."""
    companion = DEFAULT_COMPANION_NAMES.get(section, f"{section}.md")
    pointer = pointer_overrides.get(section) or DEFAULT_POINTERS.get(section,
                                                                     f"See [{companion}]({companion}).")
    return (
        ["--doc", str(doc), "--section", section, "--companion-name", companion, "--pointer", pointer],
        companion,
    )


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Audit/split skill-doc metadata sections into companion files."
    )
    parser.add_argument("--target", required=True,
                        help="a skill directory (contains SKILL.md) or a library root to sweep recursively")
    parser.add_argument("--sections", default=",".join(DEFAULT_SECTIONS),
                        help=f"comma-separated section names (default: {','.join(DEFAULT_SECTIONS)})")
    parser.add_argument("--pointer", action="append", default=[], metavar="SECTION=TEXT",
                        help="override the pointer paragraph for a section (repeatable, e.g. "
                             "--pointer 'Traceability=See [TRACEABILITY.md](TRACEABILITY.md) for provenance.'; "
                             "defaults: Changelog -> 'See [CHANGELOG.md](CHANGELOG.md).', "
                             "Traceability -> 'See [TRACEABILITY.md](TRACEABILITY.md).')")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="report inline sections; exit 1 if any")
    mode.add_argument("--dry-run", action="store_true", help="print the split plan without writing")
    mode.add_argument("--split", action="store_true", help="split all inline sections, then re-audit")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 2:
            return 2
        raise

    target = Path(args.target)
    sections = [s.strip() for s in args.sections.split(",") if s.strip()]
    if not sections:
        print("separate-skill-doc-metadata: --sections is empty", file=sys.stderr)
        return 2

    pointer_overrides: Dict[str, str] = {}
    for item in args.pointer:
        if "=" not in item:
            print(f"separate-skill-doc-metadata: --pointer must be SECTION=TEXT: {item!r}",
                  file=sys.stderr)
            return 2
        section, text = item.split("=", 1)
        pointer_overrides[section.strip()] = text

    try:
        violations = audit(target, sections)
    except FileNotFoundError as error:
        print(f"separate-skill-doc-metadata: {error}", file=sys.stderr)
        return 1

    if args.check:
        if violations:
            print(f"separate-skill-doc-metadata: {len(violations)} inline section(s) found:")
            for doc, section in violations:
                print(f"  {doc}: '## {section}'")
            return 1
        print("separate-skill-doc-metadata: compliant — no inline metadata sections.")
        return 0

    if args.dry_run:
        for doc, section in violations:
            args_list, companion = plan_split(doc, section, pointer_overrides)
            proc = run_base(base_script(), args_list + ["--dry-run"])
            if proc.returncode != 0:
                print(f"separate-skill-doc-metadata: dry-run failed for {doc} "
                      f"({section}): {proc.stderr.strip()}", file=sys.stderr)
                return 1
            print(f"{proc.stdout.rstrip()}  -> companion {companion}")
        print(f"separate-skill-doc-metadata: {len(violations)} split(s) planned.")
        return 0

    failures = 0
    for doc, section in violations:
        args_list, companion = plan_split(doc, section, pointer_overrides)
        proc = run_base(base_script(), args_list + ["--split"])
        if proc.returncode != 0:
            failures += 1
            print(f"separate-skill-doc-metadata: split failed for {doc} "
                  f"({section}): {proc.stderr.strip()}", file=sys.stderr)
            continue
        print(f"{proc.stdout.rstrip()}")

    remaining = audit(target, sections)
    if failures or remaining:
        print(f"separate-skill-doc-metadata: {failures} split failure(s), "
              f"{len(remaining)} inline section(s) remaining — re-run to inspect.", file=sys.stderr)
        return 1
    print(f"separate-skill-doc-metadata: {len(violations)} section(s) split; "
          "re-audit clean — compliant.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
