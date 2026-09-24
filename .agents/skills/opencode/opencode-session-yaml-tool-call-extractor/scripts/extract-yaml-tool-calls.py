#!/usr/bin/env python3
"""
OpenCode Session YAML Tool-Call Extractor

Extract every assistant tool call (tool, args, result) from opencode
logger-plugin YAML logs. Two input layouts are supported:

1. Monolithic file: `.opencode/logs/ses_<id>.yaml` — multi-document YAML,
   `---` separated. First document is the session header (has a `session:`
   key); subsequent documents are turns (`user:` / `assistant:`).
2. Per-turn directory: `.opencode/logs/ses_<id>/` — one file per turn,
   `000-header-*.yaml` + `NNN-<timestamp>.yaml`. Filename order equals
   chronological order.

Output: JSONL, one record per tool call, in chronological order:
{"index": N, "tool": "...", "args": {...}, "result": "..."}

Tier-1 (Python) per scripting-language-selection-rules §3.1 — YAML/JSON
parsing and file I/O.
"""

import argparse
import json
import sys
from pathlib import Path

import yaml


def _normalize_list(value):
    """Normalize a single-dict-or-list value to a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _iter_tool_calls_from_docs(docs, start_index):
    """Yield (index, tool_call) pairs for every assistant tool_call in docs."""
    index = start_index
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        for entry in _normalize_list(doc.get("assistant")):
            if not isinstance(entry, dict):
                continue
            for call in _normalize_list(entry.get("tool_calls")):
                if not isinstance(call, dict):
                    continue
                yield index, {
                    "index": index,
                    "tool": call.get("tool"),
                    "args": call.get("args"),
                    "result": call.get("result"),
                }
                index += 1


def _parse_stream(stream_text, source_name, errors):
    """Parse a YAML stream, returning (docs, error_flag)."""
    try:
        return list(yaml.safe_load_all(stream_text)), False
    except yaml.YAMLError as exc:
        errors.append(f"YAML parse error in {source_name}: {exc}")
        return [], True


def extract_tool_calls(input_path: Path):
    """Collect every tool call from a monolithic file or per-turn directory."""
    calls = []
    errors = []
    index = 0

    if input_path.is_dir():
        files = sorted(input_path.glob("*.yaml"))
        if not files:
            errors.append(f"No *.yaml files found in directory: {input_path}")
        for file_path in files:
            docs, had_error = _parse_stream(
                file_path.read_text(encoding="utf-8"), str(file_path), errors
            )
            for index, call in _iter_tool_calls_from_docs(docs, index):
                calls.append(call)
    elif input_path.is_file():
        docs, had_error = _parse_stream(
            input_path.read_text(encoding="utf-8"), str(input_path), errors
        )
        for index, call in _iter_tool_calls_from_docs(docs, index):
            calls.append(call)
    else:
        errors.append(f"Input path not found: {input_path}")

    return calls, errors


def write_jsonl(calls, output):
    lines = [json.dumps(c, ensure_ascii=False) + "\n" for c in calls]
    if output:
        output.write_text("".join(lines), encoding="utf-8")
    else:
        sys.stdout.write("".join(lines))


def main():
    parser = argparse.ArgumentParser(
        description="Extract tool calls (tool, args, result) from opencode "
        "logger-plugin YAML logs — monolithic file or per-turn directory"
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to a monolithic ses_<id>.yaml file OR a per-turn "
        "ses_<id>/ directory of NNN-*.yaml files",
    )
    parser.add_argument(
        "--tool",
        action="append",
        default=[],
        help="Filter to one tool name (repeatable; e.g. --tool write --tool edit)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSONL to file instead of stdout",
    )

    args = parser.parse_args()
    tool_filters = set(args.tool)

    if not args.input.exists():
        print(f"Error: Input path not found: {args.input}", file=sys.stderr)
        sys.exit(3)

    try:
        calls, errors = extract_tool_calls(args.input)
    except Exception as exc:
        print(f"Error: Failed to parse input: {exc}", file=sys.stderr)
        sys.exit(2)

    for error in errors:
        print(f"Warning: {error}", file=sys.stderr)

    if tool_filters:
        before = len(calls)
        calls = [c for c in calls if c.get("tool") in tool_filters]
        print(
            f"Filtered {before} tool calls to {len(calls)} matching "
            f"{sorted(tool_filters)}",
            file=sys.stderr,
        )

    if not calls:
        print("No tool calls found matching criteria", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(calls)} tool call(s)", file=sys.stderr)
    write_jsonl(calls, args.output)

    if args.output:
        print(f"JSONL written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
