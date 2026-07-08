#!/usr/bin/env python3
"""
OpenCode Session Edit Extractor

Extract Tool: edit JSON payloads (filePath + oldString + newString) from
opencode session export markdown files.

Tier-1 (Python) per scripting-language-selection-rules §3.1 — pure text
parsing, regex, JSON, file I/O.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterator


def extract_edit_payloads(session_path: Path) -> list[dict]:
    """Extract Tool: edit payloads from an opencode session markdown file.

    Returns a list of dicts with 'filePath', 'oldString', and 'newString' keys.
    """
    text = session_path.read_text(encoding="utf-8")

    payloads: list[dict] = []

    for match in re.finditer(
        r'\*\*Tool: edit\*\*\s*\n\s*\n'
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
        old_string = data.get("oldString")
        new_string = data.get("newString")
        if not file_path or old_string is None or new_string is None:
            print(
                f"Warning: Skipping payload at position {match.start()}: "
                "missing filePath, oldString, or newString",
                file=sys.stderr,
            )
            continue

        payloads.append({
            "filePath": file_path,
            "oldString": old_string,
            "newString": new_string,
        })

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
        description="Extract Tool: edit JSON payloads from opencode session export files"
    )
    parser.add_argument(
        "--session",
        required=True,
        type=Path,
        help="Path to opencode session export (.md)",
    )
    parser.add_argument(
        "--file-pattern",
        help="Glob pattern to filter edit payloads by filePath "
        "(e.g., '**/AGENTS.md')",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSONL to file instead of stdout",
    )

    args = parser.parse_args()

    if not args.session.exists():
        print(
            f"Error: Session file not found: {args.session}", file=sys.stderr
        )
        sys.exit(3)

    try:
        payloads = extract_edit_payloads(args.session)
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
        print("No edit payloads found matching criteria", file=sys.stderr)
        sys.exit(1)

    print(
        f"Found {len(payloads)} edit payload(s)", file=sys.stderr
    )
    write_jsonl(payloads, args.output)

    if args.output:
        print(f"JSONL written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
