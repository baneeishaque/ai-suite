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


# Heredoc capture: cat (>/>>) <path> << 'DELIMITER'\n<content>\nDELIMITER
HEREDOC_RE = re.compile(
    r"cat\s+(>|>>)\s+(\S+)\s*<<\s*'(\w+)'\s*\n(.*?)\n\3",
    re.DOTALL,
)


def extract_writes_from_commands(commands: list[str]) -> list[dict]:
    """Run the heredoc parser over a list of bash command strings.

    Shared core for the .md and YAML input modes.
    """
    writes: list[dict] = []

    for command in commands:
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


def extract_bash_writes(session_path: Path) -> list[dict]:
    """Extract file-write operations from Tool: bash blocks.

    Returns a list of dicts with 'filePath', 'content', and 'mode' keys.
    """
    text = session_path.read_text(encoding="utf-8")

    commands: list[str] = []

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

        commands.append(command)

    return extract_writes_from_commands(commands)


def extract_bash_writes_from_yaml(yaml_path: Path) -> list[dict]:
    """Extract heredoc file writes from logger-plugin YAML logs.

    Delegates tool-call discovery to the opencode-session-yaml-tool-call-
    extractor base skill, then runs the shared heredoc parser over each
    `bash` call's command string.
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

    commands: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if is_rejected(record):
            continue
        command = record.get("args", {}).get("command", "")
        if command:
            commands.append(command)

    return extract_writes_from_commands(commands)


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

    source = args.session or args.yaml
    if not source.exists():
        print(
            f"Error: Session file not found: {source}", file=sys.stderr
        )
        sys.exit(3)

    try:
        if args.yaml:
            writes = extract_bash_writes_from_yaml(args.yaml)
        else:
            writes = extract_bash_writes(args.session)
    except FileNotFoundError as exc:
        print(f"Error: Session file not found: {exc}", file=sys.stderr)
        sys.exit(3)
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
