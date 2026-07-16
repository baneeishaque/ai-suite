#!/usr/bin/env python3
"""
Session Full Change Audit

Layer 3+ composer — runs every change-extractor against an opencode session
export and produces a unified, mergeable JSONL audit stream plus a
consolidated human-readable report.

Covers four change sources:
  1. Tool: write    → opencode-session-write-extractor
  2. Tool: edit     → opencode-session-edit-extractor
  3. Tool: bash file ops → opencode-session-bash-block-extractor +
                           opencode-session-bash-file-ops-classifier
  4. Tool: bash heredoc writes → opencode-session-bash-write-extractor

Tier-1 (Python) per scripting-language-selection-rules §3.1 — pure
text parsing, subprocess dispatch, JSON, file I/O.
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
AGENTS_DIR = SKILL_DIR.parent

WRITE_EXTRACTOR = (
    AGENTS_DIR
    / "opencode-session-write-extractor"
    / "scripts"
    / "extract-session-writes.py"
)
EDIT_EXTRACTOR = (
    AGENTS_DIR
    / "opencode-session-edit-extractor"
    / "scripts"
    / "extract-session-edits.py"
)
BASH_BLOCK_EXTRACTOR = (
    AGENTS_DIR
    / "opencode-session-bash-block-extractor"
    / "scripts"
    / "extract-bash-blocks.py"
)
BASH_FILE_CLASSIFIER = (
    AGENTS_DIR
    / "opencode-session-bash-file-ops-classifier"
    / "scripts"
    / "classify-bash-file-ops.py"
)
BASH_WRITE_EXTRACTOR = (
    AGENTS_DIR
    / "opencode-session-bash-write-extractor"
    / "scripts"
    / "extract-bash-writes.py"
)

SOURCE_MAP = {
    "write": WRITE_EXTRACTOR,
    "edit": EDIT_EXTRACTOR,
    "bash-write": BASH_WRITE_EXTRACTOR,
}


def check_scripts(sources: list[str]) -> None:
    for src in sources:
        if src == "bash":
            if not BASH_BLOCK_EXTRACTOR.exists():
                print(
                    f"Error: bash-block-extractor not found: "
                    f"{BASH_BLOCK_EXTRACTOR}",
                    file=sys.stderr,
                )
                sys.exit(2)
            if not BASH_FILE_CLASSIFIER.exists():
                print(
                    f"Error: bash-file-classifier not found: "
                    f"{BASH_FILE_CLASSIFIER}",
                    file=sys.stderr,
                )
                sys.exit(2)
        else:
            path = SOURCE_MAP.get(src)
            if path and not path.exists():
                print(
                    f"Error: script not found for source '{src}': {path}",
                    file=sys.stderr,
                )
                sys.exit(2)


def run_extractor(
    script_path: Path, session_path: Path, source_tag: str
) -> list[dict]:
    args = [sys.executable, str(script_path), "--session", str(session_path)]
    try:
        proc = subprocess.run(
            args, capture_output=True, text=True, check=False
        )
    except OSError as exc:
        print(
            f"Error: Failed to run {script_path.name}: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)

    results: list[dict] = []
    if proc.returncode in (0, 1) and proc.stdout.strip():
        for line in proc.stdout.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                item["_source"] = source_tag
                results.append(item)
            except json.JSONDecodeError:
                print(
                    f"Warning: Skipping unparseable JSONL from "
                    f"{script_path.name}",
                    file=sys.stderr,
                )
    return results


def run_bash_pipeline(session_path: Path) -> list[dict]:
    args = [
        sys.executable, str(BASH_BLOCK_EXTRACTOR), "--session",
        str(session_path),
    ]
    try:
        extract_proc = subprocess.run(
            args, capture_output=True, text=True, check=False
        )
    except OSError as exc:
        print(
            f"Error: Failed to run bash-block-extractor: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)

    if (
        extract_proc.returncode not in (0, 1)
        or not extract_proc.stdout.strip()
    ):
        return []

    classify_args = [sys.executable, str(BASH_FILE_CLASSIFIER)]
    try:
        classify_proc = subprocess.run(
            classify_args,
            input=extract_proc.stdout,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        print(
            f"Error: Failed to run bash-file-classifier: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)

    if (
        classify_proc.returncode not in (0, 1)
        or not classify_proc.stdout.strip()
    ):
        return []

    results: list[dict] = []
    for line in classify_proc.stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
            item["_source"] = "bash-op"
            results.append(item)
        except json.JSONDecodeError:
            print(
                "Warning: Skipping unparseable JSONL from classifier",
                file=sys.stderr,
            )
    return results


def generate_report(all_ops: list[dict], session_path: Path) -> str:
    lines: list[str] = []
    lines.append("# Session Full Change Audit")
    lines.append("")
    lines.append(f"**Session**: {session_path.name}")
    lines.append(f"**Total changes**: {len(all_ops)}")
    lines.append("")

    source_counter: Counter[str] = Counter()
    for op in all_ops:
        source_counter[op.get("_source", "unknown")] += 1

    lines.append("## Summary by Source")
    lines.append("")
    lines.append("| Source | Count |")
    lines.append("|---|---|")
    for src, count in sorted(source_counter.items()):
        lines.append(f"| {src} | {count} |")
    lines.append("")

    bash_ops = [op for op in all_ops if op.get("_source") == "bash-op"]
    if bash_ops:
        op_counter: Counter[str] = Counter()
        for op in bash_ops:
            op_counter[op.get("operation", "unknown")] += 1
        lines.append("### Bash File Operations Detail")
        lines.append("")
        lines.append("| Operation | Count |")
        lines.append("|---|---|")
        for op_type, count in sorted(op_counter.items()):
            lines.append(f"| {op_type} | {count} |")
        lines.append("")

    for src in ["write", "edit", "bash-write", "bash-op"]:
        filtered = [op for op in all_ops if op.get("_source") == src]
        if not filtered:
            continue
        lines.append(f"## {src.title()} Changes")
        lines.append("")
        if src in ("write", "bash-write"):
            lines.append("| # | File | Content Preview |")
            lines.append("|---|---|---|")
            for i, op in enumerate(filtered, 1):
                fpath = op.get("filePath", "—")
                content = op.get("content", "")
                preview = (
                    content[:60].replace("\n", "\\n") if content else "—"
                )
                lines.append(f"| {i} | `{fpath}` | `{preview}` |")
        elif src == "edit":
            lines.append("| # | File | oldString Preview | newString Preview |")
            lines.append("|---|---|---|---|")
            for i, op in enumerate(filtered, 1):
                fpath = op.get("filePath", "—")
                old = (op.get("oldString", "") or "")[:40].replace(
                    "\n", "\\n"
                )
                new = (op.get("newString", "") or "")[:40].replace(
                    "\n", "\\n"
                )
                lines.append(
                    f"| {i} | `{fpath}` | `{old}` | `{new}` |"
                )
        elif src == "bash-op":
            lines.append("| # | Operation | Target | Source |")
            lines.append("|---|---|---|---|")
            for i, op in enumerate(filtered, 1):
                op_type = op.get("operation", "—")
                target = op.get("target") or "—"
                source = op.get("source") or "—"
                lines.append(
                    f"| {i} | {op_type} | `{target}` | `{source}` |"
                )
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Audit ALL changes from an opencode session export — "
        "covers Tool: write, Tool: edit, Tool: bash file operations, "
        "and Tool: bash heredoc writes"
    )
    parser.add_argument(
        "--session",
        required=True,
        type=Path,
        help="Path to opencode session export (.md)",
    )
    parser.add_argument(
        "--source",
        choices=["write", "edit", "bash", "bash-write", "all"],
        default="all",
        help="Filter by change source type (default: all)",
    )
    parser.add_argument(
        "--output-jsonl",
        type=Path,
        help="Write unified JSONL stream to file",
    )
    parser.add_argument(
        "--output-report",
        type=Path,
        help="Write human-readable report to file",
    )

    args = parser.parse_args()

    if not args.session.exists():
        print(
            f"Error: Session file not found: {args.session}",
            file=sys.stderr,
        )
        sys.exit(3)

    if args.source == "all":
        sources = ["write", "edit", "bash", "bash-write"]
    else:
        sources = [args.source]

    check_scripts(sources)

    all_ops: list[dict] = []

    for src in sources:
        if src == "bash":
            all_ops.extend(run_bash_pipeline(args.session))
        else:
            path = SOURCE_MAP.get(src)
            if path:
                all_ops.extend(
                    run_extractor(path, args.session, src)
                )

    if not all_ops:
        print("No changes found in session")
        sys.exit(1)

    report = generate_report(all_ops, args.session)
    print(report)

    if args.output_report:
        args.output_report.write_text(report, encoding="utf-8")
        print(
            f"\nReport written to: {args.output_report}",
            file=sys.stderr,
        )

    if args.output_jsonl:
        jsonl_lines = [
            json.dumps(op, ensure_ascii=False) + "\n" for op in all_ops
        ]
        args.output_jsonl.write_text(
            "".join(jsonl_lines), encoding="utf-8"
        )
        print(
            f"JSONL written to: {args.output_jsonl}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
