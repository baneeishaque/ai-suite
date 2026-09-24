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
import subprocess
import sys
from pathlib import Path

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


def extract_bash_blocks_from_yaml(yaml_path: Path) -> list[dict]:
    """Extract bash commands from logger-plugin YAML logs.

    Delegates tool-call discovery to the opencode-session-yaml-tool-call-
    extractor base skill, then maps each `bash` call's args onto the same
    {'command'} contract as the .md parser.
    """
    proc = subprocess.run(
        [
            sys.executable,
            str(BASE_YAML_EXTRACTOR),
            "--input",
            str(yaml_path),
            "--tool",
            "bash",
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode == 3:
        raise FileNotFoundError(str(yaml_path))
    if proc.returncode == 2:
        raise RuntimeError(f"YAML parse failure: {proc.stderr.strip()}")

    blocks: list[dict] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if is_rejected(record):
            continue
        command = record.get("args", {}).get("command", "")
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
        "--output",
        type=Path,
        help="Write JSONL to file instead of stdout",
    )

    args = parser.parse_args()

    source = args.session or args.yaml
    if not source.exists():
        print(
            f"Error: Session file not found: {source}",
            file=sys.stderr,
        )
        sys.exit(3)

    try:
        if args.yaml:
            blocks = extract_bash_blocks_from_yaml(args.yaml)
        else:
            blocks = extract_bash_blocks(args.session)
    except FileNotFoundError as exc:
        print(f"Error: Session file not found: {exc}", file=sys.stderr)
        sys.exit(3)
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
