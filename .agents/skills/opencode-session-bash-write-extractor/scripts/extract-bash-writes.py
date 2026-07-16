#!/usr/bin/env python3
"""
OpenCode Session Bash Write Extractor

Extract file-write operations from Tool: bash command strings in opencode
session export markdown files. Handles heredoc patterns:

    cat > /path/to/file << 'DELIM'
    <content>
    DELIM
    cat >> /path/to/file << 'DELIM'
    <content>
    DELIM

Tier-1 (Python) per scripting-language-selection-rules §3.1 — pure text
parsing, regex, JSON, file I/O.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterator


# Heredoc capture: cat (>/>>) <path> << 'DELIMITER'\n<content>\nDELIMITER
HEREDOC_RE = re.compile(
    r"cat\s+(>|>>)\s+(\S+)\s*<<\s*'(\w+)'\s*\n(.*?)\n\3",
    re.DOTALL,
)


def extract_bash_writes(session_path: Path) -> list[dict]:
    """Extract file-write operations from Tool: bash blocks.

    Returns a list of dicts with 'filePath', 'content', and 'mode' keys.
    """
    text = session_path.read_text(encoding="utf-8")

    writes: list[dict] = []

    for match in re.finditer(
        r'\*\*Tool: bash\*\*\s*\n\s*\n'
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

        command = data.get("command", "")
        if not command:
            continue

        for h_match in HEREDOC_RE.finditer(command):
            op = h_match.group(1)  # '>' or '>>'
            raw_path = h_match.group(2)
            delimiter = h_match.group(3)
            content = h_match.group(4)

            # Resolve relative paths (command likely executed from repo root)
            # If path is absolute, use as-is; otherwise skip (cannot resolve
            # reliably from session export alone)
            if not os.path.isabs(raw_path):
                print(
                    f"Warning: Skipping relative path '{raw_path}' "
                    f"(delimiter '{delimiter}') — cannot resolve without "
                    "knowing working directory",
                    file=sys.stderr,
                )
                continue

            writes.append({
                "filePath": raw_path,
                "content": content,
                "mode": "overwrite" if op == ">" else "append",
            })

    return writes


def filter_by_pattern(
    writes: list[dict], pattern: str
) -> list[dict]:
    """Filter writes whose filePath matches the given glob pattern."""
    import fnmatch

    return [w for w in writes if fnmatch.fnmatch(w["filePath"], pattern)]


def filter_by_mode(writes: list[dict], mode: str) -> list[dict]:
    """Filter writes by mode (overwrite, append, or all)."""
    if mode == "all":
        return writes
    return [w for w in writes if w["mode"] == mode]


def write_jsonl(writes: list[dict], output: Path | None):
    """Write writes as JSONL to stdout or to a file."""
    lines = [json.dumps(w, ensure_ascii=False) + "\n" for w in writes]

    if output:
        output.write_text("".join(lines), encoding="utf-8")
    else:
        sys.stdout.write("".join(lines))


def main():
    parser = argparse.ArgumentParser(
        description="Extract file writes from Tool: bash commands in opencode session export files"
    )
    parser.add_argument(
        "--session",
        required=True,
        type=Path,
        help="Path to opencode session export (.md)",
    )
    parser.add_argument(
        "--file-pattern",
        help="Glob pattern to filter writes by filePath "
        "(e.g., '**/scripts/*.py')",
    )
    parser.add_argument(
        "--mode",
        choices=["overwrite", "append", "all"],
        default="all",
        help="Filter by operation type (default: all)",
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
        writes = extract_bash_writes(args.session)
    except Exception as exc:
        print(
            f"Error: Failed to parse session file: {exc}", file=sys.stderr
        )
        sys.exit(2)

    if args.file_pattern:
        before = len(writes)
        writes = filter_by_pattern(writes, args.file_pattern)
        print(
            f"Filtered {before} writes to {len(writes)} "
            f"matching '{args.file_pattern}'",
            file=sys.stderr,
        )

    writes = filter_by_mode(writes, args.mode)
    print(
        f"Mode filter '{args.mode}': {len(writes)} write(s) remaining",
        file=sys.stderr,
    )

    if not writes:
        print("No matching bash file writes found", file=sys.stderr)
        sys.exit(1)

    print(
        f"Found {len(writes)} bash file write(s)", file=sys.stderr
    )
    write_jsonl(writes, args.output)

    if args.output:
        print(f"JSONL written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
