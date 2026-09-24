#!/usr/bin/env python3
"""
OpenCode Session Bash File Ops Classifier

Classify bash command strings into file operation types.

Reads JSONL from stdin (or --input file), where each line is
{"command": "..."}. Outputs one JSONL line per classified file
operation.

Operation types:
  - write:   cat > /path << 'DELIM'\n<content>\nDELIM
  - write:   printf/echo ... > /path (shell redirect)
  - append:  cat >> /path << 'DELIM'\n<content>\nDELIM
  - append:  printf/echo ... >> /path (shell redirect)
  - delete:  rm, rm -rf, rm -f, git rm
  - copy:    cp
  - move:    mv, git mv
  - other:   commands not matching any file-operation pattern

Tier-1 (Python) per scripting-language-selection-rules §3.1 — pure
text parsing, regex, JSON, file I/O.
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

# Redirect write: printf/echo ... > <path>. The `>` must NOT be an fd
# redirect (2>) and its target must look like a path (contain `/`, `.`,
# or start with `~`) — so prose like `<path>` inside format strings or
# stderr suppression never matches.
REDIRECT_RE = re.compile(
    r"\b(?:echo|printf)\b.*?(?<![0-9])(>>|>)\s*(?=[^\s;&|]*[/.~])([^\s;&|]+)",
    re.DOTALL,
)


OP_PATTERNS: list[tuple[str, type[re.Pattern]]] = [
    # Order matters: more specific first
    ("delete", re.compile(r'^git\s+rm\s+(-r\s+)?(-f\s+)?(\S+)')),
    ("delete", re.compile(r'^rm\s+(-rf\s+)?(-r\s+)?(-f\s+)?(\S+)')),
    ("copy", re.compile(r'^cp\s+(-r\s+)?(-f\s+)?(\S+)\s+(\S+)')),
    ("move", re.compile(r'^git\s+mv\s+(\S+)\s+(\S+)')),
    ("move", re.compile(r'^mv\s+(\S+)\s+(\S+)')),
]


def classify_command(command: str) -> list[dict]:
    """Classify a single bash command string into file operation(s).

    Returns a list of operation dicts (most commands produce 1, but
    a single cat chain could produce multiple writes).
    """
    results: list[dict] = []

    # Check for heredoc writes (cat >/>>) — multiple per command
    for h_match in HEREDOC_RE.finditer(command):
        op = h_match.group(1)
        raw_path = h_match.group(2).strip('"')
        content = h_match.group(4)
        resolved = raw_path if os.path.isabs(raw_path) else None
        results.append({
            "command": command,
            "operation": "overwrite" if op == ">" else "append",
            "target": resolved or raw_path,
            "source": None,
            "content": content,
        })

    if results:
        return results

    # Check for redirect writes (printf/echo > file)
    for r_match in REDIRECT_RE.finditer(command):
        op = r_match.group(1)
        raw_path = r_match.group(2).strip('"')
        if raw_path == "/dev/null":
            continue
        if "\\" in raw_path:
            # Escaped targets (e.g. `\".agents/...` inside a python -c
            # string) are shell text embedded in a quoted program, not
            # real redirects.
            continue
        if "/" not in raw_path and not raw_path.startswith((".", "~")):
            continue
        resolved = raw_path if os.path.isabs(raw_path) else None
        results.append({
            "command": command,
            "operation": "overwrite" if op == ">" else "append",
            "target": resolved or raw_path,
            "source": None,
            "content": None,
        })

    if results:
        return results

    # Check for other operation patterns
    for op_type, pattern in OP_PATTERNS:
        m = pattern.search(command)
        if m:
            groups = m.groups()
            if op_type == "delete":
                # Last non-None group is the target path
                target = [g for g in groups if g is not None][-1]
                resolved = target if os.path.isabs(target) else None
                results.append({
                    "command": command,
                    "operation": op_type,
                    "target": resolved or target,
                    "source": None,
                    "content": None,
                })
                return results
            elif op_type == "copy":
                # Second-to-last non-None is source, last is target
                non_none = [g for g in groups if g is not None]
                source = non_none[-2]
                target = non_none[-1]
                results.append({
                    "command": command,
                    "operation": op_type,
                    "target": target,
                    "source": source,
                    "content": None,
                })
                return results
            elif op_type == "move":
                source = groups[-2] if groups[-2] else groups[-1]
                target = groups[-1]
                results.append({
                    "command": command,
                    "operation": op_type,
                    "target": target,
                    "source": source if source != target else None,
                    "content": None,
                })
                return results

    # No file operation detected
    results.append({
        "command": command,
        "operation": "other",
        "target": None,
        "source": None,
        "content": None,
    })
    return results


def read_commands(input_path: Path | None) -> Iterator[dict]:
    """Read JSONL lines from stdin or input file."""
    if input_path:
        with open(input_path, encoding="utf-8") as f:
            for line in f:
                yield json.loads(line)
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def commands_from_yaml(yaml_path: Path) -> list[dict]:
    """Fetch bash commands from logger-plugin YAML logs.

    Delegates tool-call discovery to the opencode-session-yaml-tool-call-
    extractor base skill, then maps each `bash` call's args onto the
    classifier's {'command'} input contract.
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

    commands: list[dict] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if is_rejected(record):
            continue
        command = record.get("args", {}).get("command", "")
        if command:
            commands.append({"command": command})
    return commands


def main():
    parser = argparse.ArgumentParser(
        description="Classify bash command strings into file operation types"
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="JSONL input file (default: stdin)",
    )
    parser.add_argument(
        "--yaml",
        type=Path,
        help="Path to opencode logger-plugin YAML log (monolithic "
        ".yaml file OR per-turn directory) — mutually exclusive with --input",
    )
    parser.add_argument(
        "--operation",
        choices=["write", "append", "overwrite", "delete", "copy", "move",
                 "other", "all"],
        default="all",
        help="Filter output by operation type (default: all)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSONL to file instead of stdout",
    )

    args = parser.parse_args()

    if args.input and args.yaml:
        print("Error: --input and --yaml are mutually exclusive", file=sys.stderr)
        sys.exit(2)

    try:
        if args.yaml:
            commands = commands_from_yaml(args.yaml)
        else:
            commands = list(read_commands(args.input))
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSONL input: {exc}", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input or args.yaml}", file=sys.stderr)
        sys.exit(3)

    if not commands:
        print("No commands to classify", file=sys.stderr)
        sys.exit(1)

    all_ops: list[dict] = []
    for entry in commands:
        command = entry.get("command", "")
        if not command:
            continue
        all_ops.extend(classify_command(command))

    # Filter by operation type
    if args.operation != "all":
        before = len(all_ops)
        all_ops = [op for op in all_ops if op["operation"] == args.operation]
        print(
            f"Filtered {before} ops to {len(all_ops)} "
            f"type '{args.operation}'",
            file=sys.stderr,
        )

    if not all_ops:
        print("No matching file operations found", file=sys.stderr)
        sys.exit(1)

    print(
        f"Classified {len(all_ops)} file operation(s)", file=sys.stderr
    )

    lines = [
        json.dumps(op, ensure_ascii=False) + "\n" for op in all_ops
    ]
    if args.output:
        args.output.write_text("".join(lines), encoding="utf-8")
        print(f"JSONL written to: {args.output}", file=sys.stderr)
    else:
        sys.stdout.write("".join(lines))


if __name__ == "__main__":
    main()
