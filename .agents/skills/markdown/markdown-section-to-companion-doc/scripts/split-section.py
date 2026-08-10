#!/usr/bin/env python3
"""Move a named `## Section` from a markdown doc into a sibling companion file.

Tier 1 (Python) per scripting-language-selection-rules.md Section 3: a
line-oriented markdown transform needing structured detection and validation;
standard library only, zero external dependencies. Runs on any Python >= 3.10.

Domain-agnostic primitive: given a markdown document and a section name, it

- CHECK:  reports whether the `## <Name>` section is INLINE (body content
  present) or external (absent, or a pointer-only `See [X.md](X.md).` stub),
  with exact line ranges.
- SPLIT:  extracts an inline section body into a sibling `<NAME>.md` companion
  document (`# <Section> — <doc-stem>` title + body) and replaces the inline
  block with the heading plus a pointer paragraph.
- DRY-RUN: prints the planned companion file and the source replacement range
  without writing anything.

The transform is idempotent: splitting an already-external section is a no-op.

Exit codes:
  0  success / no-op / compliant (section absent or external)
  1  inline section found (--check) / section not found (--split)
  2  usage or IO error
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

HEADING_RE = re.compile(r"^##\s+(\S.*?)\s*$")
POINTER_RE = re.compile(r"^See\s+\[[^\]]*\.md")


def _read_lines(path: Path) -> List[str]:
    return path.read_text(encoding="utf-8").splitlines(keepends=False)


def _write_lines(path: Path, lines: List[str]) -> None:
    text = "\n".join(lines)
    if text:
        text += "\n"
    path.write_text(text, encoding="utf-8")


def find_section(lines: List[str], name: str) -> Optional[Tuple[int, int]]:
    """Return (start, end) line indexes of the `## <name>` section, or None."""
    start: Optional[int] = None
    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match and match.group(1).strip() == name:
            start = index
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if HEADING_RE.match(lines[index]):
            end = index
            break
    return start, end


def section_body(lines: List[str], span: Tuple[int, int]) -> List[str]:
    """Body of the section, leading/trailing blank lines stripped."""
    body = lines[span[0] + 1 : span[1]]
    while body and body[-1] == "":
        body.pop()
    while body and body[0] == "":
        body.pop(0)
    return body


def is_pointer_only(body: List[str]) -> bool:
    """True when the body is pointer prose pointing at a companion file.

    Rule: the first non-empty line starts with `See [X.md` (a markdown link to a
    companion .md file — backtick-quoted link styles allowed) AND the body
    contains no structured content (bullets, numbered items, table rows, fenced
    code blocks). Wrapped prose continuation lines are allowed — pointer prose
    is typically 1-3 sentences that may span lines.
    """
    non_empty = [line for line in body if line.strip()]
    if not non_empty:
        return False
    if not POINTER_RE.match(non_empty[0]):
        return False
    structured = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|\||```)")
    return not any(structured.match(line) for line in non_empty)


def title_stem_for(path: Path) -> str:
    """Companion title stem: parent dir for SKILL.md/AGENTS.md, else file stem."""
    if path.name in ("SKILL.md", "AGENTS.md"):
        return path.parent.name
    return path.stem


def split_plan(
    doc: Path,
    section: str,
    pointer: str,
    companion_name: str,
) -> Optional[Tuple[Path, List[str], List[str], List[str]]]:
    """Plan the split: (companion_path, companion_lines, new_source_lines, old_lines).

    Returns None when the section is absent or already external (no-op).
    """
    lines = _read_lines(doc)
    span = find_section(lines, section)
    if span is None:
        return None
    body = section_body(lines, span)
    if is_pointer_only(body):
        return None

    companion = doc.parent / companion_name
    companion_lines = [f"# {section} — {title_stem_for(doc)}", ""] + body + [""]

    new_source = lines[: span[0]] + [f"## {section}", "", pointer] + [""] + lines[span[1] :]
    return companion, companion_lines, new_source, lines


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Move a named ## Section from a markdown doc into a sibling companion file."
    )
    parser.add_argument("--doc", required=True, help="path to the markdown document")
    parser.add_argument("--section", required=True, help="section name (e.g. Traceability)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="report whether the section is inline (exit 1 if so)")
    mode.add_argument("--split", action="store_true", help="extract the inline section into a companion file")
    mode.add_argument("--dry-run", action="store_true", help="print the planned split without writing")
    parser.add_argument("--pointer", default=None, help="pointer paragraph placed under the retained heading (default: 'See [<companion>.md](<companion>.md).')")
    parser.add_argument("--companion-name", default=None, help="companion filename (default: <Section>.md)")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 2:
            return 2
        raise

    doc = Path(args.doc)
    if not doc.is_file():
        print(f"split-section: doc not found: {doc}", file=sys.stderr)
        return 2

    companion_name = args.companion_name or f"{args.section}.md"
    pointer = args.pointer or f"See [{companion_name}]({companion_name})."

    try:
        lines = _read_lines(doc)
    except OSError as error:
        print(f"split-section: cannot read {doc}: {error}", file=sys.stderr)
        return 2

    span = find_section(lines, args.section)
    if span is None:
        if args.check:
            return 0
        print(f"split-section: section '## {args.section}' not present in {doc}", file=sys.stderr)
        return 1

    body = section_body(lines, span)
    if is_pointer_only(body):
        if args.check:
            return 0
        return 0

    if args.check:
        print(f"INLINE  {doc}: '## {args.section}' at lines {span[0] + 1}-{span[1]} "
              f"({len(body)} body line(s))")
        return 1

    companion = doc.parent / companion_name
    if args.dry_run:
        print(f"SPLIT   {doc}: '## {args.section}' (lines {span[0] + 1}-{span[1]})")
        print(f"  -> companion {companion}  (title: '# {args.section} — {title_stem_for(doc)}')")
        print(f"  -> source replaced with '## {args.section}' + pointer: {pointer}")
        return 0

    new_source = lines[: span[0]] + [f"## {args.section}", "", pointer] + [""] + lines[span[1] :]
    try:
        _write_lines(companion, [f"# {args.section} — {title_stem_for(doc)}", ""] + body + [""])
        _write_lines(doc, new_source)
    except OSError as error:
        print(f"split-section: write failed: {error}", file=sys.stderr)
        return 2
    print(f"SPLIT   {doc}: '## {args.section}' -> {companion}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
