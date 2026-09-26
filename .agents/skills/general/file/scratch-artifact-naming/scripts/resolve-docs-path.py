#!/usr/bin/env python3
"""Resolve a docs-scoped artifact path per custom organisation.

Formula:
  <repo-root>/docs/<session-id>/<date>/<purpose>/<artifact>_v<version>_<time>.<ext>

- <session-id> : full opencode session ID without `ses_` prefix (auto-discovered).
- <date>       : YYYY-MM-DD directory (IST by default).
- <purpose>    : lowercase-kebab directory (e.g. pr-812, teams-extract).
- <artifact>   : lowercase-kebab file stem prefix (e.g. diff, review, files, test-sweep).
- _v<version>  : optional version segment (e.g. _v1).
- <time>       : HH-MM-SS-mmm_TZ (milliseconds + timezone, IST default).
- <ext>        : file extension without dot (e.g. md, json, diff).

Composes opencode-current-session-id discovery for session ID.
Timezone handling uses zoneinfo (Python 3.9+); falls back to UTC if unavailable.
"""
from __future__ import annotations
import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

SCRIPT_DIR = Path(__file__).resolve().parent
FIND_SESSION = SCRIPT_DIR.parents[3] / "opencode/opencode-current-session-id/scripts/find-current-session.py"

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SESSION_RE = re.compile(r"^[a-z0-9]+$", re.IGNORECASE)


def discover_session_id() -> str | None:
    if not FIND_SESSION.is_file():
        return None
    try:
        r = subprocess.run([sys.executable, str(FIND_SESSION)], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    for line in r.stdout.splitlines():
        if line.startswith("Session ID: "):
            sid = line.split(":", 1)[1].strip()
            if sid.startswith("ses_"):
                sid = sid[4:]
            return sid
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Resolve docs/<session>/<date>/<purpose>/<artifact>_v<ver>_<time>.<ext>")
    ap.add_argument("--repo", default=".", help="Repo root (default: CWD)")
    ap.add_argument("--purpose", required=True, help="Lowercase-kebab purpose directory")
    ap.add_argument("--artifact", required=True, help="Lowercase-kebab artifact file prefix")
    ap.add_argument("--version", type=int, help="Version number for _v<version> segment")
    ap.add_argument("--ext", required=True, help="File extension without dot (e.g. md, json, diff)")
    ap.add_argument("--session-id", help="Full opencode session ID (ses_ prefix optional); auto-discovered when omitted")
    ap.add_argument("--date", help="YYYY-MM-DD override (default: now in --timezone)")
    ap.add_argument("--timezone", default="Asia/Kolkata", help="IANA timezone for date/time (default: Asia/Kolkata IST)")
    ap.add_argument("--timestamp", help="HH-MM-SS-mmm_TZ override (tests); if provided, used verbatim")
    ap.add_argument("--no-mkdir", action="store_true", help="Print without creating directories")
    args = ap.parse_args()

    if not KEBAB_RE.match(args.purpose):
        print(f"ERROR: --purpose must be lowercase-kebab: {args.purpose!r}", file=sys.stderr)
        return 1
    if not KEBAB_RE.match(args.artifact):
        print(f"ERROR: --artifact must be lowercase-kebab: {args.artifact!r}", file=sys.stderr)
        return 1
    if args.version is not None and args.version < 1:
        print("ERROR: --version must be >= 1", file=sys.stderr)
        return 1
    if not re.fullmatch(r"[a-z0-9]+", args.ext):
        print(f"ERROR: --ext must be alphanumeric without dot: {args.ext!r}", file=sys.stderr)
        return 1

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"ERROR: repo directory not found: {repo}", file=sys.stderr)
        return 1

    session_id = args.session_id
    if session_id:
        if session_id.startswith("ses_"):
            session_id = session_id[4:]
    else:
        session_id = discover_session_id()
        if not session_id:
            print("ERROR: could not discover session id; pass --session-id", file=sys.stderr)
            return 1

    try:
        tz = ZoneInfo(args.timezone)
    except Exception as exc:
        print(f"ERROR: invalid --timezone {args.timezone!r}: {exc}", file=sys.stderr)
        return 1

    now = datetime.datetime.now(tz)
    date_str = args.date or now.strftime("%Y-%m-%d")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
        print(f"ERROR: --date must be YYYY-MM-DD: {date_str!r}", file=sys.stderr)
        return 1

    # Time with milliseconds + timezone abbreviation or offset
    if args.timestamp:
        time_str = args.timestamp
    else:
        # HH-MM-SS-mmm_TZ where mmm is milliseconds, TZ is zone abbreviation (e.g. IST)
        ms = f"{now.microsecond // 1000:03d}"
        # Abbreviation via %Z, fallback to offset
        tz_abbr = now.strftime("%Z") or now.strftime("%z") or args.timezone
        # Sanitize abbreviation for filename (: and + not ideal but keep + and -)
        tz_abbr = tz_abbr.replace("/", "-")
        time_str = f"{now.strftime('%H-%M-%S')}-{ms}_{tz_abbr}"

    version_seg = f"_v{args.version}" if args.version is not None else ""
    filename = f"{args.artifact}{version_seg}_{time_str}.{args.ext}"
    out_dir = repo / "docs" / session_id / date_str / args.purpose
    out_path = out_dir / filename

    if not args.no_mkdir:
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print(f"ERROR: could not create docs directory: {exc}", file=sys.stderr)
            return 1

    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
