#!/usr/bin/env python3
"""
OpenCode Session Write Extractor

Extract Tool: write JSON payloads (filePath + content) from opencode session
export markdown files.

Tier-1 (Python) per scripting-language-selection-rules §3.1 — pure text
parsing, regex, JSON, file I/O.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterator


BASE_YAML_EXTRACTOR = (
    Path(__file__).resolve().parent.parent.parent
    / "opencode"
    / "opencode-session-yaml-tool-call-extractor"
    / "scripts"
    / "extract-yaml-tool-calls.py"
)

REJECTED_RESULT_MARKER = (
    "The user rejected permission to use this specific tool call."
)


def is_rejected(record: dict) -> bool:
    """True when a YAML tool-call record was rejected by the user."""
    result = record.get("result")
    return isinstance(result, str) and REJECTED_RESULT_MARKER in result


def extract_write_payloads(session_path: Path) -> list[dict]:
    """Extract Tool: write payloads from an opencode session markdown file.

    Returns a list of dicts with 'filePath' and 'content' keys.
    """
    text = session_path.read_text(encoding="utf-8")

    payloads: list[dict] = []

    for match in re.finditer(
        r'\*\*Tool: write\*\*\s*\n\s*\n'
        r'\*\*Input:\*\*\s*\n'
        r'```json\s*\n'
        r'(\{.*?\})\s*\n'
        r'```',
        text,
        re.DOTALL,
    ):
        raw_json = match.group(1)
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            print(
                f"Warning: JSON parse error at position {match.start()}: {exc}",
                file=sys.stderr,
            )
            continue

        file_path = data.get("filePath")
        content = data.get("content")
        if not file_path or content is None:
            print(
                f"Warning: Skipping payload at position {match.start()}: "
                "missing filePath or content",
                file=sys.stderr,
            )
            continue

        payloads.append({"filePath": file_path, "content": content})

    return payloads


def extract_write_payloads_from_yaml(yaml_path: Path) -> list[dict]:
    """Extract write payloads from logger-plugin YAML logs.

    Delegates tool-call discovery to the opencode-session-yaml-tool-call-
    extractor base skill, then maps each `write` call's args onto the same
    {'filePath', 'content'} contract as the .md parser.
    """
    proc = subprocess.run(
        [
            sys.executable,
            str(BASE_YAML_EXTRACTOR),
            "--input",
            str(yaml_path),
            "--tool",
            "write",
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode == 3:
        raise FileNotFoundError(str(yaml_path))
    if proc.returncode == 2:
        raise RuntimeError(f"YAML parse failure: {proc.stderr.strip()}")

    payloads: list[dict] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if is_rejected(record):
            continue
        args = record.get("args", {})
        file_path = args.get("filePath")
        content = args.get("content")
        if not file_path or content is None:
            continue
        payloads.append({"filePath": file_path, "content": content})
    return payloads


def filter_by_pattern(
    payloads: list[dict], pattern: str
) -> list[dict]:
    """Filter payloads whose filePath matches the given glob pattern."""
    import fnmatch

    return [
        p for p in payloads if fnmatch.fnmatch(p["filePath"], pattern)
    ]


def write_jsonl(payloads: list[dict], output: Path | None):
    """Write payloads as JSONL to stdout or to a file."""
    lines = [json.dumps(p, ensure_ascii=False) + "\n" for p in payloads]

    if output:
        output.write_text("".join(lines), encoding="utf-8")
    else:
        sys.stdout.write("".join(lines))


def main():
    parser = argparse.ArgumentParser(
        description="Extract Tool: write JSON payloads from opencode session export files"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--session",
        type=Path,
        help="Path to opencode session export (.md)",
    )
    group.add_argument(
        "--yaml",
        type=Path,
        help="Path to opencode logger-plugin YAML log "
        "(monolithic .yaml file OR per-turn directory)",
    )
    parser.add_argument(
        "--file-pattern",
        help="Glob pattern to filter write payloads by filePath "
        "(e.g., '**/implementation-plans/*.md')",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSONL to file instead of stdout",
    )

    args = parser.parse_args()

    source = args.session or args.yaml
    if not source.exists():
        print(
            f"Error: Session file not found: {source}", file=sys.stderr
        )
        sys.exit(3)

    try:
        if args.yaml:
            payloads = extract_write_payloads_from_yaml(args.yaml)
        else:
            payloads = extract_write_payloads(args.session)
    except FileNotFoundError as exc:
        print(f"Error: Session file not found: {exc}", file=sys.stderr)
        sys.exit(3)
    except Exception as exc:
        print(
            f"Error: Failed to parse session file: {exc}", file=sys.stderr
        )
        sys.exit(2)

    if args.file_pattern:
        before = len(payloads)
        payloads = filter_by_pattern(payloads, args.file_pattern)
        print(
            f"Filtered {before} payloads to {len(payloads)} "
            f"matching '{args.file_pattern}'",
            file=sys.stderr,
        )

    if not payloads:
        print("No write payloads found matching criteria", file=sys.stderr)
        sys.exit(1)

    print(
        f"Found {len(payloads)} write payload(s)", file=sys.stderr
    )
    write_jsonl(payloads, args.output)

    if args.output:
        print(f"JSONL written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
