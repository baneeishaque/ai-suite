#!/usr/bin/env python3
"""Resolve opencode session transcript references to their source log files.

Composer over `file-glob-sort-by-regex-capture`. Given free text containing
opencode session-log references (transcript form
`.../ses_<id>/transcripts/NNN-<ts>-transcript.yaml`, source form
`.../ses_<id>/NNN-<ts>.yaml`), each optionally followed by a `to N` range
marker, this script:

  * rewrites each reference to its SOURCE form (strip `-transcript`, ascend
    out of `transcripts/`), reproducing the chat-natural compact expression
    verbatim;
  * with --expand, expands `to N` ranges to the full list of absolute source
    log paths by delegating to the base skill's sort-by-capture.py
    (--min/--max numeric span filter) — never re-implementing the
    glob+regex+sort pipeline.

Usage:
  resolve-transcript-refs.py --text "<reference text>" [--expand] [--output FILE]

Exit codes:
  0  success (at least one reference resolved)
  1  no session-log references found in --text
  2  usage / parse error, or base script (sort-by-capture.py) missing
  3  referenced session dir or source file not found (--expand only)

stdout carries ONLY the payload (safe to pipe); diagnostics go to stderr.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Optional, Sequence, Tuple

# Composer lives at .agents/skills/opencode/<skill>/scripts/.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
_BASE_REL = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "..",
    "file-glob-sort-by-regex-capture",
    "scripts",
    "sort-by-capture.py",
)
_BASE_SCRIPT = os.path.abspath(_BASE_REL)

# A session-log reference token: optional leading path (absolute, `...`-abbrev,
# or bare), session id, optional /transcripts, numbered source file, and an
# optional ` to N` range marker. The path may be wrapped in backticks or
# quotes (chat export artifacts).
_REF_RE = re.compile(
    r"(?:[`\"'])?"
    r"(?P<path>\S*?ses_[A-Za-z0-9]+(?:/transcripts)?/(?P<num>\d{3})-[^\s/]+\.yaml)"
    r"(?:[`\"'])?"
    r"(?:\s+to\s+(?P<to>\d{1,4}))?"
)


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve opencode session transcript references to source logs"
    )
    parser.add_argument(
        "--text",
        required=True,
        help="Free text containing opencode session-log references "
        "(transcript or source form, optional `to N` ranges)",
    )
    parser.add_argument(
        "--expand",
        action="store_true",
        help="Emit one absolute source-log path per line; ranges are expanded "
        "via the base skill's numeric-span filter",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write payload to this file instead of stdout",
    )
    return parser.parse_args(argv)


def _parse_reference(match: "re.Match[str]") -> Tuple[str, str, int, Optional[int]]:
    """Return (session_dir, source_filename, start_number, end_number)."""
    path = match.group("path")
    num = match.group("num")
    stamp = os.path.basename(path)[len(num) + 1 :]
    is_transcript = stamp.endswith("-transcript.yaml")
    source_basename = num + "-" + stamp[: -len("-transcript.yaml")] + ".yaml" if is_transcript else num + "-" + stamp

    dirname = os.path.dirname(path)
    if dirname.endswith("/transcripts") or dirname.endswith("/transcripts/"):
        session_dir = os.path.dirname(dirname)
    else:
        session_dir = dirname

    to_val = match.group("to")
    end_number: Optional[int] = int(to_val) if to_val is not None else None
    return session_dir, source_basename, int(num), end_number


def _find_session_dir(session_dir: str) -> Optional[str]:
    """Resolve the session directory on disk, handling `...`-abbrev / bare refs."""
    if os.path.isdir(session_dir):
        return os.path.abspath(session_dir)
    session_id = re.search(r"ses_[A-Za-z0-9]+$", session_dir)
    if session_id is None:
        return None
    for candidate in (
        os.path.join(_REPO_ROOT, ".opencode", "logs", session_id.group(0)),
        os.path.join(_REPO_ROOT, session_id.group(0)),
    ):
        if os.path.isdir(candidate):
            return os.path.abspath(candidate)
    return None


def _expand_range(session_dir: str, start: int, end: int) -> list[str]:
    """Delegate the numeric span listing to the base skill's sort-by-capture.py."""
    if not os.path.isfile(_BASE_SCRIPT):
        sys.stderr.write(
            f"error: base script not found: {_BASE_SCRIPT}\n"
            "install the file-glob-sort-by-regex-capture skill library first\n"
        )
        sys.exit(2)
    cmd = [
        sys.executable,
        _BASE_SCRIPT,
        "--directory",
        session_dir,
        "--glob",
        "0*-*.yaml",
        "--regex",
        r"^(\d{3})-",
        "--sort-type",
        "int",
        "--min",
        str(start),
        "--max",
        str(end),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 2:
        sys.stderr.write(f"error: base script usage error: {proc.stderr.strip()}\n")
        sys.exit(2)
    if proc.returncode != 0:
        sys.stderr.write(f"error: base script failed (exit {proc.returncode}): {proc.stderr.strip()}\n")
        sys.exit(3)
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    return [json.loads(line)["abspath"] for line in lines]


def _write_payload(payload: str, output: Optional[str]) -> None:
    if output is None:
        sys.stdout.write(payload)
    else:
        with open(output, "w", encoding="utf-8") as handle:
            handle.write(payload)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)
    matches = list(_REF_RE.finditer(args.text))
    if not matches:
        sys.stderr.write("error: no opencode session-log references found in --text\n")
        return 1

    payload_lines: list[str] = []
    for match in matches:
        session_dir, source_basename, start_number, end_number = _parse_reference(match)
        source_ref = f"{session_dir}/{source_basename}"
        if end_number is None:
            if args.expand:
                real_dir = _find_session_dir(session_dir)
                if real_dir is None:
                    sys.stderr.write(f"error: session directory not found: {session_dir}\n")
                    return 3
                source_path = os.path.join(real_dir, source_basename)
                if not os.path.isfile(source_path):
                    sys.stderr.write(f"error: source file not found: {source_path}\n")
                    return 3
                payload_lines.append(source_path)
            else:
                payload_lines.append(source_ref)
        else:
            if args.expand:
                real_dir = _find_session_dir(session_dir)
                if real_dir is None:
                    sys.stderr.write(f"error: session directory not found: {session_dir}\n")
                    return 3
                payload_lines.extend(_expand_range(real_dir, start_number, end_number))
            else:
                payload_lines.append(f"{source_ref} to {end_number}")

    _write_payload("\n".join(payload_lines) + "\n", args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
