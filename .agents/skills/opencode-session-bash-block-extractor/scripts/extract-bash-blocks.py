#!/usr/bin/env python3
"""
OpenCode Session Bash Block Extractor

Extract raw Tool: bash command strings from opencode session export
markdown files. Outputs one JSONL line per Tool: bash block found.

This is a domain-agnostic base primitive — it only finds bash blocks
and extracts the command string. It does NOT classify or interpret
the command.

Tier-1 (Python) per scripting-language-selection-rules §3.1 — pure
text parsing, regex, JSON, file I/O.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Matches: **Tool: bash**\n\n**Input:**\n```json\n{"command": "..."}\n```
TOOL_BASH_RE = re.compile(
    r'\*\*Tool: bash\*\*\s*\n\s*\n'
    r'\*\*Input:\*\*\s*\n'
    r'```json\s*\n'
    r'(\{.*?\})\s*\n'
    r'```',
    re.DOTALL,
)


def extract_bash_blocks(session_path: Path) -> list[dict]:
    """Extract bash command strings from Tool: bash blocks.

    Returns a list of dicts with a single 'command' key each.
    """
    text = session_path.read_text(encoding="utf-8")
    blocks: list[dict] = []

    for match in TOOL_BASH_RE.finditer(text):
        raw_json = match.group(1)
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            print(
                f"Warning: JSON parse error at position "
                f"{match.start()}: {exc}",
                file=sys.stderr,
            )
            continue

        command = data.get("command", "")
        if command:
            blocks.append({"command": command})

    return blocks


def write_jsonl(blocks: list[dict], output: Path | None):
    """Write blocks as JSONL to stdout or to a file."""
    lines = [json.dumps(b, ensure_ascii=False) + "\n" for b in blocks]
    if output:
        output.write_text("".join(lines), encoding="utf-8")
    else:
        sys.stdout.write("".join(lines))


def main():
    parser = argparse.ArgumentParser(
        description="Extract Tool: bash command strings from opencode "
        "session export files"
    )
    parser.add_argument(
        "--session",
        required=True,
        type=Path,
        help="Path to opencode session export (.md)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSONL to file instead of stdout",
    )

    args = parser.parse_args()

    if not args.session.exists():
        print(
            f"Error: Session file not found: {args.session}",
            file=sys.stderr,
        )
        sys.exit(3)

    try:
        blocks = extract_bash_blocks(args.session)
    except Exception as exc:
        print(
            f"Error: Failed to parse session file: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)

    if not blocks:
        print("No Tool: bash blocks found", file=sys.stderr)
        sys.exit(1)

    print(
        f"Found {len(blocks)} Tool: bash block(s)", file=sys.stderr
    )
    write_jsonl(blocks, args.output)

    if args.output:
        print(f"JSONL written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
