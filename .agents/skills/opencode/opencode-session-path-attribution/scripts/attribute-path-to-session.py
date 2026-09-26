#!/usr/bin/env python3
"""Cross-session opencode logger attribution by path token.

Sweeps opencode logger-plugin per-turn session logs
(.opencode/logs/ses_<id>/NNN-<timestamp>.yaml), consumes the
opencode-session-yaml-tool-call-extractor CLI stdout JSONL for every turn
file, and emits each tool call whose stringified `args` contain ALL of the
required --path tokens (substring match, case-sensitive).

Output: one JSON object per stdout line (JSONL) unless --json (array).
Record:
{"session_id": str, "timestamp": ISO, "file": turn-file-name,
 "tool": str, "index": int, "args": dict, "match": [tokens]}

Exit codes:
- 0: at least one match found
- 1: no matches in the scanned calls (and no infrastructure failure)
- 2: usage error / missing dependency (extractor or locator), or I/O error

Usage:
  attribute-path-to-session.py [--logs <dir>] [--session <id> ...]
      --path <token> ... [--tool <name> ...] [--since <ISO>] [--until <ISO>]
      [--json] [--output <file>]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[4]  # .agents/skills/opencode/<skill>/scripts

EXTRACTOR = (
    REPO_ROOT
    / ".agents/skills/opencode/opencode-session-yaml-tool-call-extractor"
    / "scripts/extract-yaml-tool-calls.py"
)
LOCATOR = (
    REPO_ROOT
    / ".agents/skills/opencode/opencode-installed-plugin-lookup"
    / "scripts/locate-installed-plugins.py"
)

TURN_RE = re.compile(r"^\d{3}-([0-9TZ\-\.]+)\.yaml$")


def turn_timestamp(name: str) -> datetime | None:
    """Turn filename 'NNN-2026-08-07T04-14-05-689Z.yaml' -> aware UTC dt.

    Returns None for header files (000-header-*) or unparseable names.
    """
    m = TURN_RE.match(name)
    if not m:
        return None
    s = m.group(1)
    try:
        iso = f"{s[0:10]}T{s[11:13]}:{s[14:16]}:{s[17:19]}.{s[20:23]}+00:00"
        return datetime.fromisoformat(iso)
    except (ValueError, IndexError):
        return None


def parse_iso(text: str | None) -> datetime | None:
    """Parse a user-supplied ISO datetime; naive values are treated as UTC."""
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def discover_logs_dir() -> Path:
    """Locate the logger output convention via Base #2 (never re-implement
    the locator). Falls back to the repo-relative default."""
    if LOCATOR.is_file():
        try:
            r = subprocess.run(
                [sys.executable, str(LOCATOR), "--plugin", "logger", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(REPO_ROOT),
            )
            if r.returncode == 0:
                for entry in json.loads(r.stdout):
                    if entry.get("name") == "logger" and entry.get("logs_dir"):
                        return Path(entry["logs_dir"])
        except (json.JSONDecodeError, subprocess.SubprocessError, OSError):
            pass
    return REPO_ROOT / ".opencode" / "logs"


def query_turn(turn_file: Path, tool_filters: list[str]) -> list[dict]:
    """Shell out to the extractor CLI; consume its stdout JSONL."""
    cmd = [sys.executable, str(EXTRACTOR), "--input", str(turn_file)]
    for tool in tool_filters:
        cmd += ["--tool", tool]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        print(f"WARN: extractor timeout for {turn_file.name}", file=sys.stderr)
        return []
    if r.returncode == 3:
        print(f"WARN: extractor input not found: {turn_file.name}", file=sys.stderr)
        return []
    records: list[dict] = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def scan_session(
    session_dir: Path,
    tokens: list[str],
    tool_filters: list[str],
    since: datetime | None,
    until: datetime | None,
) -> list[dict]:
    """Emit attribution cards for every matching call in a session dir."""
    hits: list[dict] = []
    for turn_file in sorted(session_dir.iterdir()):
        if not turn_file.is_file():
            continue
        ts = turn_timestamp(turn_file.name)
        if ts is None:  # 000-header-* or unparseable
            continue
        if since and ts < since:
            continue
        if until and ts > until:
            continue
        for rec in query_turn(turn_file, tool_filters):
            args_str = json.dumps(rec.get("args", {}), ensure_ascii=False)
            matched = [t for t in tokens if t in args_str]
            if len(matched) == len(tokens):
                hits.append(
                    {
                        "session_id": session_dir.name[len("ses_"):],
                        "timestamp": ts.isoformat(),
                        "file": turn_file.name,
                        "tool": rec.get("tool"),
                        "index": rec.get("index"),
                        "args": rec.get("args"),
                        "match": matched,
                    }
                )
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(
        description="attribute logger tool calls to sessions by path token",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--logs", help="logger logs dir (default: discovered)")
    ap.add_argument("--session", action="append", default=[],
                    help="session id to restrict to (ses_ prefix optional); repeatable")
    ap.add_argument("--path", action="append", default=[], required=True,
                    metavar="TOKEN", help="token required in stringified args; repeatable")
    ap.add_argument("--tool", action="append", default=[],
                    help="only consider calls of this tool; repeatable")
    ap.add_argument("--since", help="only turn files at/after this ISO time (UTC)")
    ap.add_argument("--until", help="only turn files at/before this ISO time (UTC)")
    ap.add_argument("--json", action="store_true",
                    help="emit one JSON array instead of JSONL")
    ap.add_argument("--output", help="write to this file instead of stdout")
    args = ap.parse_args()

    since = parse_iso(args.since)
    until = parse_iso(args.until)
    if args.since and since is None:
        print(f"ERROR: cannot parse --since '{args.since}'", file=sys.stderr)
        return 2
    if args.until and until is None:
        print(f"ERROR: cannot parse --until '{args.until}'", file=sys.stderr)
        return 2
    if not EXTRACTOR.is_file():
        print(f"ERROR: extractor not found: {EXTRACTOR}", file=sys.stderr)
        return 2

    logs_dir = Path(args.logs) if args.logs else discover_logs_dir()
    if not logs_dir.is_dir():
        print(f"ERROR: logs dir not found: {logs_dir}", file=sys.stderr)
        return 2

    wanted = {s if s.startswith("ses_") else f"ses_{s}" for s in args.session}
    session_dirs = [
        d
        for d in sorted(
            (d for d in logs_dir.iterdir() if d.is_dir() and d.name.startswith("ses_")),
            key=lambda d: d.stat().st_mtime,
            reverse=True,
        )
    ]
    if wanted:
        session_dirs = [d for d in session_dirs if d.name in wanted]
        for missing in sorted(wanted - {d.name for d in session_dirs}):
            print(f"WARN: no session dir for '{missing}'", file=sys.stderr)

    hits = []
    for d in session_dirs:
        hits.extend(scan_session(d, args.path, args.tool, since, until))

    if args.json:
        text = json.dumps(hits, ensure_ascii=False, indent=2)
    else:
        text = "".join(json.dumps(h, ensure_ascii=False) + "\n" for h in hits)

    if args.output:
        Path(args.output).write_text(text)
        print(f"Wrote {len(hits)} record(s) to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())