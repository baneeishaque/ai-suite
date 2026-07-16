#!/usr/bin/env python3
"""
Aggregate session audit reports across multiple session files or pre-existing
JSONL files into one consolidated cross-reference report.

Two input modes (mutually exclusive):
  1. --session-dir <dir>   Run audit-full-change.py on every .md file,
                           capture JSONL per file, and aggregate.
  2. --jsonl-dir <dir>     Merge pre-existing JSONL files (one per session)
                           into a unified report; _session derived from
                           filename stem.

Output: merged JSONL stream (--output-jsonl) + human-readable aggregate
report (--output-report). Prints report to stdout when neither is given.

Tier-1 (Python) per scripting-language-selection-rules §3.1 — pure text
parsing, subprocess, JSON, file I/O.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
AGENTS_DIR = SKILL_DIR.parent

AUDIT_SCRIPT = (
    AGENTS_DIR / "session-full-change-audit" / "scripts" / "audit-full-change.py"
)


def collect_from_sessions(
    session_dir: Path, glob_pattern: str
) -> list[dict]:
    """Run audit-full-change.py per session .md, tag JSONL with _session."""
    if not AUDIT_SCRIPT.exists():
        print(
            f"Error: session-full-change-audit script not found: {AUDIT_SCRIPT}",
            file=sys.stderr,
        )
        sys.exit(2)

    results: list[dict] = []
    session_files = sorted(session_dir.glob(glob_pattern))
    if not session_files:
        print(
            f"Warning: No session files matching '{glob_pattern}' "
            f"in {session_dir}",
            file=sys.stderr,
        )
        return results

    for session_file in session_files:
        session_name = session_file.stem

        with tempfile.NamedTemporaryFile(
            suffix=".jsonl", delete=False, mode="w"
        ) as tmp:
            jsonl_path = Path(tmp.name)

        args = [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--session",
            str(session_file),
            "--output-jsonl",
            str(jsonl_path),
        ]
        try:
            proc = subprocess.run(
                args, capture_output=True, text=True, check=False
            )
        except OSError as exc:
            print(
                f"Warning: Failed to audit {session_file.name}: {exc}",
                file=sys.stderr,
            )
            jsonl_path.unlink(missing_ok=True)
            continue

        if proc.returncode not in (0, 1):
            print(
                f"Warning: audit-full-change.py exited {proc.returncode} "
                f"for {session_file.name}",
                file=sys.stderr,
            )
            jsonl_path.unlink(missing_ok=True)
            continue

        try:
            text = jsonl_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(
                f"Warning: Cannot read JSONL for {session_file.name}: "
                f"{exc}",
                file=sys.stderr,
            )
            jsonl_path.unlink(missing_ok=True)
            continue

        jsonl_path.unlink(missing_ok=True)

        if not text.strip():
            continue

        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                item["_session"] = session_name
                results.append(item)
            except json.JSONDecodeError:
                print(
                    f"Warning: Skipping unparseable JSONL line from "
                    f"{session_file.name}",
                    file=sys.stderr,
                )

    print(
        f"Collected {len(results)} change records from "
        f"{len(session_files)} session files",
        file=sys.stderr,
    )
    return results


def collect_from_jsonl(jsonl_dir: Path, glob_pattern: str) -> list[dict]:
    """Read pre-existing JSONL files, derive _session from filename stem."""
    results: list[dict] = []
    jsonl_files = sorted(jsonl_dir.glob(glob_pattern))
    if not jsonl_files:
        print(
            f"Warning: No JSONL files matching '{glob_pattern}' "
            f"in {jsonl_dir}",
            file=sys.stderr,
        )
        return results

    for jsonl_file in jsonl_files:
        session_name = jsonl_file.stem
        try:
            text = jsonl_file.read_text(encoding="utf-8")
        except OSError as exc:
            print(
                f"Warning: Cannot read {jsonl_file.name}: {exc}",
                file=sys.stderr,
            )
            continue

        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                item["_session"] = session_name
                results.append(item)
            except json.JSONDecodeError:
                print(
                    f"Warning: Skipping unparseable JSONL line from "
                    f"{jsonl_file.name}",
                    file=sys.stderr,
                )

    print(
        f"Merged {len(results)} change records from "
        f"{len(jsonl_files)} JSONL files",
        file=sys.stderr,
    )
    return results


def generate_aggregate_report(all_ops: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# Consolidated Session Full Change Audit")
    lines.append("")

    writes = [
        op
        for op in all_ops
        if op.get("_source") in ("write", "bash-write")
    ]
    edits = [op for op in all_ops if op.get("_source") == "edit"]
    bash_ops = [op for op in all_ops if op.get("_source") == "bash-op"]

    unique_writes: set[str] = set()
    write_sessions: dict[str, set[str]] = {}
    for op in writes:
        fp = op.get("filePath", "")
        if fp:
            unique_writes.add(fp)
            write_sessions.setdefault(fp, set()).add(
                op.get("_session", "")
            )

    unique_edits: set[str] = set()
    edit_sessions: dict[str, set[str]] = {}
    edit_count: dict[str, int] = {}
    for op in edits:
        fp = op.get("filePath", "")
        if fp:
            unique_edits.add(fp)
            edit_count[fp] = edit_count.get(fp, 0) + 1
            edit_sessions.setdefault(fp, set()).add(
                op.get("_session", "")
            )

    deletes = [
        op for op in bash_ops if op.get("operation") == "delete"
    ]
    delete_sessions: dict[str, set[str]] = {}
    delete_count: dict[str, int] = {}
    for op in deletes:
        target = op.get("target", "")
        if target:
            delete_count[target] = delete_count.get(target, 0) + 1
            delete_sessions.setdefault(target, set()).add(
                op.get("_session", "")
            )

    total_bash = len(bash_ops)
    total_deletes = sum(delete_count.values())
    total_other = total_bash - total_deletes

    all_sessions = sorted(
        set(
            op.get("_session", "")
            for op in all_ops
            if op.get("_session")
        )
    )
    session_count = len(all_sessions)

    session_line = f"**Sessions**: {', '.join(all_sessions)} ({session_count} total)" if all_sessions else "**Sessions**: (none)"
    lines.append(session_line)
    lines.append(f"**Unique files created**: {len(unique_writes)}")
    lines.append(f"**Unique files modified**: {len(unique_edits)}")
    lines.append(
        f"**Total edit operations**: {sum(edit_count.values())}"
    )
    lines.append(
        f"**Total bash operations**: {total_bash} "
        f"({total_deletes} deletes, {total_other} other)"
    )
    lines.append(
        f"**Files deleted**: {len(delete_count)} "
        f"({total_deletes} delete operations)"
    )
    lines.append("")

    lines.append("## Summary by Source")
    lines.append("")
    lines.append("| Source | Count |")
    lines.append("|---|---|")
    lines.append(f"| write (new files) | {len(unique_writes)} |")
    lines.append(
        f"| edit (files modified) | {len(unique_edits)} |"
    )
    lines.append(
        f"| bash delete | {len(delete_count)} unique files |"
    )
    lines.append(f"| bash other | {total_other} ops |")
    lines.append("")

    if unique_writes:
        lines.append("## Write Changes — Files Created")
        lines.append("")
        lines.append("| # | File | Sessions |")
        lines.append("|---|---|---|")
        for i, fp in enumerate(sorted(unique_writes), 1):
            sessions = ", ".join(
                sorted(write_sessions.get(fp, set()))
            )
            lines.append(f"| {i} | `{fp}` | {sessions} |")
        lines.append("")

    if unique_edits:
        lines.append("## Edit Changes — Files Modified")
        lines.append("")
        lines.append("| # | File | Edit Ops | Sessions |")
        lines.append("|---|---|---|---|")
        for i, fp in enumerate(sorted(unique_edits), 1):
            ops = edit_count.get(fp, 0)
            sessions = ", ".join(
                sorted(edit_sessions.get(fp, set()))
            )
            lines.append(
                f"| {i} | `{fp}` | {ops} | {sessions} |"
            )
        lines.append("")

    if deletes:
        lines.append("## Bash Delete Operations")
        lines.append("")
        lines.append("| # | File Deleted | Times Deleted | Sessions |")
        lines.append("|---|---|---|---|")
        for i, target in enumerate(
            sorted(delete_count.keys()), 1
        ):
            count = delete_count[target]
            sessions = ", ".join(
                sorted(delete_sessions.get(target, set()))
            )
            lines.append(
                f"| {i} | `{target}` | {count} | {sessions} |"
            )
        lines.append("")

    non_delete = [
        op
        for op in bash_ops
        if op.get("operation") != "delete"
    ]
    if non_delete:
        op_counter: Counter[str] = Counter()
        for op in non_delete:
            op_counter[op.get("operation", "unknown")] += 1
        lines.append("## Bash Other Operations")
        lines.append("")
        lines.append(
            f"{total_other} non-delete bash commands"
        )
        lines.append("")
        lines.append("| Operation | Count |")
        lines.append("|---|---|")
        for op_type, count in sorted(op_counter.items()):
            lines.append(f"| {op_type} | {count} |")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate session audit reports from multiple "
        "session files or pre-existing JSONL into one "
        "consolidated cross-reference report."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--session-dir",
        type=Path,
        help="Directory of session export .md files to audit",
    )
    group.add_argument(
        "--jsonl-dir",
        type=Path,
        help="Directory of pre-existing JSONL files to merge",
    )
    parser.add_argument(
        "--glob",
        default=None,
        help="Glob pattern for matching files "
        "(default: *.md for --session-dir, *.jsonl for --jsonl-dir)",
    )
    parser.add_argument(
        "--output-report",
        type=Path,
        help="Write consolidated report to file",
    )
    parser.add_argument(
        "--output-jsonl",
        type=Path,
        help="Write merged JSONL stream to file",
    )

    args = parser.parse_args()

    if not args.session_dir and not args.jsonl_dir:
        parser.error(
            "Either --session-dir or --jsonl-dir is required"
        )

    if args.session_dir:
        if not args.session_dir.is_dir():
            print(
                f"Error: Session directory not found: {args.session_dir}",
                file=sys.stderr,
            )
            sys.exit(3)
        glob_pattern = args.glob or "*.md"
        all_ops = collect_from_sessions(args.session_dir, glob_pattern)
    else:
        if not args.jsonl_dir.is_dir():
            print(
                f"Error: JSONL directory not found: {args.jsonl_dir}",
                file=sys.stderr,
            )
            sys.exit(3)
        glob_pattern = args.glob or "*.jsonl"
        all_ops = collect_from_jsonl(args.jsonl_dir, glob_pattern)

    if not all_ops:
        print("No changes found in any session")
        sys.exit(1)

    report = generate_aggregate_report(all_ops)
    print(report)

    if args.output_report:
        args.output_report.write_text(report, encoding="utf-8")
        print(
            f"\nReport written to: {args.output_report}",
            file=sys.stderr,
        )

    if args.output_jsonl:
        jsonl_lines = [
            json.dumps(op, ensure_ascii=False) + "\n"
            for op in all_ops
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
