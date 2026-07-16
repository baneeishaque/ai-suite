#!/usr/bin/env python3
"""
Session File Ops Audit

Composer skill — orchestrates a 2-stage pipeline:
  1. opencode-session-bash-block-extractor → extracts raw command strings
  2. opencode-session-bash-file-ops-classifier → classifies each command

Produces a human-readable report and optional JSONL output.

Tier-1 (Python) per scripting-language-selection-rules §3.1 — pure
text parsing, subprocess dispatch, JSON, file I/O.
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

# Relative paths to sibling skills' scripts
THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
AGENTS_DIR = SKILL_DIR.parent  # .agents/skills/

EXTRACTOR_SCRIPT = (
    AGENTS_DIR
    / "opencode-session-bash-block-extractor"
    / "scripts"
    / "extract-bash-blocks.py"
)
CLASSIFIER_SCRIPT = (
    AGENTS_DIR
    / "opencode-session-bash-file-ops-classifier"
    / "scripts"
    / "classify-bash-file-ops.py"
)


def find_scripts() -> dict[str, Path]:
    """Verify both extractor and classifier scripts exist. Return paths."""
    scripts = {
        "extractor": EXTRACTOR_SCRIPT,
        "classifier": CLASSIFIER_SCRIPT,
    }
    for name, path in scripts.items():
        if not path.exists():
            print(
                f"Error: {name} script not found at: {path}",
                file=sys.stderr,
            )
            sys.exit(2)
    return scripts


def run_pipeline(
    session_path: Path, operation_filter: str
) -> list[dict]:
    """Run extractor → classifier pipeline and return classified ops."""
    scripts = find_scripts()

    # Stage 1: extract bash blocks
    extractor_args = [
        sys.executable,
        str(scripts["extractor"]),
        "--session",
        str(session_path),
    ]

    try:
        extractor_proc = subprocess.run(
            extractor_args,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        print(
            f"Error: Failed to run extractor: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)

    if extractor_proc.returncode not in (0, 1):
        print(
            f"Error: Extractor exited with code "
            f"{extractor_proc.returncode}",
            file=sys.stderr,
        )
        print(extractor_proc.stderr, file=sys.stderr)
        sys.exit(2)

    if extractor_proc.returncode == 1 or not extractor_proc.stdout.strip():
        print(
            f"Session has no Tool: bash blocks — nothing to audit",
        )
        return []

    # Stage 2: classify
    classifier_args = [
        sys.executable,
        str(scripts["classifier"]),
    ]
    if operation_filter != "all":
        classifier_args.extend(["--operation", operation_filter])

    try:
        classifier_proc = subprocess.run(
            classifier_args,
            input=extractor_proc.stdout,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        print(
            f"Error: Failed to run classifier: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)

    if classifier_proc.returncode not in (0, 1):
        print(
            f"Error: Classifier exited with code "
            f"{classifier_proc.returncode}",
            file=sys.stderr,
        )
        print(classifier_proc.stderr, file=sys.stderr)
        sys.exit(2)

    if classifier_proc.returncode == 1 or not classifier_proc.stdout.strip():
        return []

    ops: list[dict] = []
    for line in classifier_proc.stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ops.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"Warning: Skipping unparseable JSONL line", file=sys.stderr)
            continue

    return ops


def generate_report(ops: list[dict], session_path: Path) -> str:
    """Generate a human-readable report from classified operations."""
    lines: list[str] = []
    lines.append(f"# Session File Operations Audit")
    lines.append(f"")
    lines.append(f"**Session**: {session_path.name}")
    lines.append(f"**Total operations**: {len(ops)}")
    lines.append(f"")

    # Summary by type
    counter: Counter[str] = Counter()
    for op in ops:
        counter[op["operation"]] += 1

    lines.append(f"## Summary")
    lines.append(f"")
    lines.append(f"| Operation Type | Count |")
    lines.append(f"|---|---|")
    for op_type, count in counter.most_common():
        lines.append(f"| {op_type} | {count} |")
    lines.append(f"")

    # Detail per operation type
    for op_type in ["delete", "overwrite", "append", "copy", "move", "other"]:
        filtered = [op for op in ops if op["operation"] == op_type]
        if not filtered:
            continue
        lines.append(f"## {op_type.title()} Operations")
        lines.append(f"")
        lines.append(f"| # | Target | Source |")
        lines.append(f"|---|---|---|")
        for i, op in enumerate(filtered, 1):
            target = op.get("target") or "—"
            source = op.get("source") or "—"
            # Truncate content for display
            content = op.get("content")
            if content:
                preview = content[:60].replace("\n", "\\n")
                target = f"{target} <<< '{preview}...'"
            lines.append(f"| {i} | `{target}` | `{source}` |")
        lines.append(f"")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Audit all file operations from an opencode session "
        "export — detect write, delete, copy, and move operations"
    )
    parser.add_argument(
        "--session",
        required=True,
        type=Path,
        help="Path to opencode session export (.md)",
    )
    parser.add_argument(
        "--operation",
        choices=["overwrite", "append", "delete", "copy", "move",
                 "other", "all"],
        default="all",
        help="Filter by operation type (also accepts 'write' as alias for 'overwrite'; default: all)",
    )
    parser.add_argument(
        "--output-jsonl",
        type=Path,
        help="Write classified operations as JSONL to file",
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

    # Map --operation "write" to "overwrite" for classifier
    op_filter = args.operation
    if op_filter == "write":
        op_filter = "overwrite"

    try:
        ops = run_pipeline(args.session, op_filter)
    except Exception as exc:
        print(
            f"Error: Pipeline failed: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)

    if not ops:
        print("No matching file operations found in session")
        sys.exit(1)

    # Generate human-readable report
    report = generate_report(ops, args.session)
    print(report)

    if args.output_report:
        args.output_report.write_text(report, encoding="utf-8")
        print(
            f"\nReport written to: {args.output_report}",
            file=sys.stderr,
        )

    # Write JSONL if requested
    if args.output_jsonl:
        jsonl_lines = [
            json.dumps(op, ensure_ascii=False) + "\n" for op in ops
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
