#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, re, subprocess, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Nearest installed copy of the opencode-current-session-id discovery script
# (same repo, resolved relative to this skill's physical location).
FIND_SESSION = SCRIPT_DIR.parents[3] / "opencode/opencode-current-session-id/scripts/find-current-session.py"

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def discover_session_id() -> str | None:
    """Run find-current-session.py and parse `Session ID: <id>`; strip a leading `ses_`."""
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
    ap = argparse.ArgumentParser(description="Resolve a session-scoped scratch artifact STEM path (no extension)")
    ap.add_argument("--repo", default=".", help="Repo root (default: CWD)")
    ap.add_argument("--purpose", required=True, help="Lowercase-kebab purpose slug")
    ap.add_argument("--session-id", help="Full opencode session ID (ses_ prefix optional); auto-discovered when omitted")
    ap.add_argument("--ref-name", help="Lower-kebab ref slug (timestamp variant implied when paired with --ref-sha)")
    ap.add_argument("--ref-sha", help="Full 40-hex commit SHA (ref variant)")
    ap.add_argument("--timestamp", help="YYYY-MM-DD_HH-MM-SS override (tests)")
    ap.add_argument("--no-mkdir", action="store_true", help="Print without creating the session directory")
    args = ap.parse_args()

    if not KEBAB_RE.match(args.purpose):
        print(f"ERROR: --purpose must be lowercase-kebab: {args.purpose!r}", file=sys.stderr)
        return 1

    if (args.ref_name is None) != (args.ref_sha is None):
        print("ERROR: --ref-name and --ref-sha must be provided together", file=sys.stderr)
        return 1

    if args.ref_sha is not None:
        if not SHA_RE.fullmatch(args.ref_sha):
            print(f"ERROR: --ref-sha must be a full 40-hex SHA: {args.ref_sha!r}", file=sys.stderr)
            return 1
        if not KEBAB_RE.match(args.ref_name):
            print(f"ERROR: --ref-name must be lowercase-kebab: {args.ref_name!r}", file=sys.stderr)
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

    session_dir = repo / "scratch" / session_id
    if not args.no_mkdir:
        try:
            session_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print(f"ERROR: could not create session directory: {exc}", file=sys.stderr)
            return 1

    if args.ref_sha:
        stem = f"{args.purpose}_{args.ref_name}_{args.ref_sha}"
    else:
        ts = args.timestamp or datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        stem = f"{args.purpose}_{ts}"

    print(session_dir / stem)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
