#!/usr/bin/env python3
"""detect-list-indent-drift.py — owned by general/list-indent-consistency.

Scan markdown files for inconsistent continuation-line indentation under
list items.  Detects drift where a continuation line uses a different
indent depth than sibling items at the same nesting level.

INPUT:  One or more file paths (positional args), or stdin (no args).
OUTPUT: Per-file drift report with line numbers and indent details.
EXIT 0: No drift found (or all drift repaired via --fix).
EXIT 1: Drift found (detection mode) or repair failure.

USAGE:
  python3 detect-list-indent-drift.py path/to/file.md
  python3 detect-list-indent-drift.py --fix path/to/file.md
  python3 detect-list-indent-drift.py .agents/skills/**/SKILL.md
  cat file.md | python3 detect-list-indent-drift.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LIST_ITEM_RE = re.compile(r'^(\s*)(\d+\.|[-*+])\s')
CONTINUATION_INDENT_RE = re.compile(r'^(\s+)\S')


def detect_drift(lines: list[str], path_str: str, fix: bool, expected_indent: int | None) -> list[str]:
    reports: list[str] = []
    modified = False
    i = 0
    n = len(lines)
    list_blocks: list[list[int]] = []

    # Phase 1: group consecutive list items into blocks.
    # A block starts at the first list item and continues until a blank line.
    # Continuation lines (non-blank, non-list-item) do NOT break the block.
    block_start = None
    for i in range(n):
        line = lines[i]
        stripped = line.rstrip()
        if not stripped:
            block_start = None
            continue
        if LIST_ITEM_RE.match(line):
            if block_start is None:
                block_start = i
                list_blocks.append([i])
            else:
                list_blocks[-1].append(i)

    # Phase 2: within each block, determine correct continuation indent
    for block in list_blocks:
        if len(block) < 2:
            continue  # single-item block can't have drift vs siblings
        # Collect continuation lines after each item in the block
        item_continuations: dict[int, list[int]] = {}
        for idx, item_line_num in enumerate(block):
            cont_lines: list[int] = []
            scan = item_line_num + 1
            while scan < n:
                if not lines[scan].strip():
                    break  # blank line ends continuation
                if LIST_ITEM_RE.match(lines[scan]):
                    break  # next list item ends continuation
                if CONTINUATION_INDENT_RE.match(lines[scan]):
                    cont_lines.append(scan)
                else:
                    break  # non-continuation content ends continuation
                scan += 1
            if cont_lines:
                item_continuations[item_line_num] = cont_lines

        # Determine correct indent from all continuation lines in this block
        all_indents: list[int] = []
        for item_line, cont_lines in item_continuations.items():
            for cl in cont_lines:
                m = CONTINUATION_INDENT_RE.match(lines[cl])
                if m:
                    all_indents.append(len(m.group(1)))
        if not all_indents:
            continue

        if expected_indent is not None:
            correct_indent = expected_indent
        else:
            from collections import Counter
            tally = Counter(all_indents)
            max_count = tally.most_common(1)[0][1]
            tied = [indent for indent, count in tally.items() if count == max_count]
            if len(tied) == 1:
                correct_indent = tied[0]
            else:
                # Tie: prefer the indent used by the first item's first continuation
                first_item = block[0]
                first_cont_lines = item_continuations.get(first_item, [])
                candidates = tied
                for cl in first_cont_lines:
                    m = CONTINUATION_INDENT_RE.match(lines[cl])
                    if m:
                        indent = len(m.group(1))
                        if indent in candidates:
                            correct_indent = indent
                            break
                else:
                    correct_indent = min(candidates)

        # Check each continuation line against correct indent
        for item_line, cont_lines in item_continuations.items():
            for cl in cont_lines:
                m = CONTINUATION_INDENT_RE.match(lines[cl])
                if not m:
                    continue
                actual_indent = len(m.group(1))
                if actual_indent == correct_indent:
                    continue
                reports.append(
                    f"[{path_str}] L{cl + 1}: expected {correct_indent} spaces, "
                    f"found {actual_indent} spaces\n  content: {lines[cl].strip()[:80]}"
                )
                if fix:
                    spaces = ' ' * correct_indent
                    content_after_indent = lines[cl][actual_indent:]
                    lines[cl] = f"{spaces}{content_after_indent}"
                    modified = True
                    reports.append(
                        f"[{path_str}] L{cl + 1}: repaired ({actual_indent} → {correct_indent} spaces)"
                    )

    if fix and modified:
        try:
            Path(path_str).write_text(''.join(lines), encoding='utf-8')
        except OSError as e:
            reports.append(f"[{path_str}] ERROR: could not write file: {e}")
            return reports

    return reports


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='*', default=None, help='Markdown file paths (stdin if omitted)')
    ap.add_argument('--fix', action='store_true', help='Repair drift in place')
    ap.add_argument('--indent', type=int, default=None,
                    help='Expected continuation indent (auto-detect from siblings if omitted)')
    ap.add_argument('--quiet', action='store_true', help='Suppress per-line output')
    args = ap.parse_args()

    paths = args.paths
    use_stdin = not paths

    if use_stdin:
        text = sys.stdin.read()
        if not text.strip():
            print("[detect-list-indent-drift] No input (stdin empty).")
            return 0
        lines = [f"{line}\n" for line in text.splitlines(keepends=False)]
        reports = detect_drift(lines, "<stdin>", args.fix, args.indent)
        drift_found = any("expected" in r for r in reports)
        if not args.quiet:
            for r in reports:
                print(r)
        if args.fix:
            return 0
        if not drift_found and not args.quiet:
            print("[detect-list-indent-drift] Clean — no indent drift found.")
        return 1 if drift_found else 0

    all_reports: list[str] = []
    for pattern in paths:
        if pattern.startswith('/'):
            file_list = [Path(pattern)]
        else:
            file_list = sorted(Path().glob(pattern))
        for p in file_list:
            if not p.is_file():
                continue
            try:
                text = p.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError) as e:
                print(f"[{p}] ERROR: {e}", file=sys.stderr)
                continue
            lines = text.splitlines(keepends=True)
            reports = detect_drift(lines, str(p), args.fix, args.indent)
            all_reports.extend(reports)

    total_drift = sum(1 for r in all_reports if "expected" in r)
    total_repaired = sum(1 for r in all_reports if "repaired" in r)

    if not args.quiet:
        for r in all_reports:
            print(r)

    if args.fix:
        if total_drift == 0 and total_repaired == 0:
            print("[detect-list-indent-drift] Clean — no indent drift found.")
            return 0
        print(f"[detect-list-indent-drift] drift={total_drift}  repaired={total_repaired}")
        return 0  # --fix exits 0 (all applicable repairs applied)

    if total_drift == 0:
        print("[detect-list-indent-drift] Clean — no indent drift found.")
        return 0

    print(f"[detect-list-indent-drift] drift={total_drift}  repaired={total_repaired}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
