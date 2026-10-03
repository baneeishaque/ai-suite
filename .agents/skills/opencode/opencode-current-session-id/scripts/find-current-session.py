#!/usr/bin/env python3
"""Discover the current opencode session ID from logger logs.

Composer: sequences file-glob-sort-by-mtime + yaml-field-extract base skills.
Selection prefers session dirs with a fresh in-flight (`*-pending-*.yaml`)
turn marker, then falls back to newest-mtime ordering.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

ENV_REPO_ROOT_VARS = ("OPENCODE_REPO_ROOT", "AI_SUITE_ROOT")
ENV_LOG_DIR_VAR = "OPENCODE_LOGS_DIR"


@lru_cache(maxsize=1)
def find_repo_root(start: Path = SCRIPT_DIR) -> Path:
    """Resolve repo root via env override, git top-level, legacy fallback.

    Cached per-process: the git rev-parse spawn dominates repeated calls.
    Call find_repo_root.cache_clear() first if $OPENCODE_REPO_ROOT or
    $AI_SUITE_ROOT may have changed since the first call.
    """
    for var in ENV_REPO_ROOT_VARS:
        val = os.environ.get(var, "").strip()
        if val:
            candidate = Path(val).expanduser().resolve()
            if candidate.is_dir():
                return candidate
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5, cwd=str(start),
        )
        if r.returncode == 0 and r.stdout.strip():
            candidate = Path(r.stdout.strip()).resolve()
            if candidate.is_dir():
                return candidate
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    if len(start.parents) >= 4:
        return start.parents[4]  # legacy: ../../../../ from scripts/
    return start.parent


def resolve_base_scripts(repo_root: Path) -> tuple[Path, Path]:
    """Locate base skill scripts, falling back to SCRIPT_DIR-relative lookup."""
    sort_p = repo_root / ".agents/skills/general/file/file-glob-sort-by-mtime/scripts/sort-by-mtime.py"
    extract_p = repo_root / ".agents/skills/general/yaml-field-extract/scripts/extract-field.py"
    if not sort_p.is_file() or not extract_p.is_file():
        if len(SCRIPT_DIR.parents) >= 3:
            agents_root = SCRIPT_DIR.parents[3]  # <root>/.agents
            alt_sort = agents_root / "skills/general/file/file-glob-sort-by-mtime/scripts/sort-by-mtime.py"
            alt_extract = agents_root / "skills/general/yaml-field-extract/scripts/extract-field.py"
            if alt_sort.is_file():
                sort_p = alt_sort
            if alt_extract.is_file():
                extract_p = alt_extract
    return sort_p, extract_p


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Discover current opencode session ID from .opencode/logs/")
    ap.add_argument("--log-dir", default=None, help="Override .opencode/logs directory (default: <repo-root>/.opencode/logs or $OPENCODE_LOGS_DIR)")
    ap.add_argument("--repo-root", default=None, help="Override repo root discovery (default: $OPENCODE_REPO_ROOT/$AI_SUITE_ROOT, git top-level, legacy parents[4])")
    ap.add_argument("--json", action="store_true", help="Emit single-line JSON instead of human-readable text")
    ap.add_argument("--state", choices=("exists", "missing", "any"), default="any",
                    help="Gate on state-file presence (default: any; mismatch exits 2)")
    ap.add_argument("--since", default=None, help="Filter sessions by st_mtime >= ISO timestamp (e.g. 2026-09-19T10:00:00)")
    ap.add_argument("--pending-ttl", type=int, default=3600,
                    help="Seconds after which an in-flight (pending) turn marker is treated as stale; 0 disables (default: 3600)")
    ap.add_argument("--dry-run", action="store_true", help="Print discovered paths (repo_root, log_dir, base scripts) and exit without extractors")
    return ap.parse_args(argv)


def run(args: list[str]) -> tuple[int, str, str]:
    """Run a base skill script; return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError as exc:
        return 127, "", f"File not found: {exc.filename}"
    except subprocess.TimeoutExpired:
        return 124, "", "Timed out"


def probe_session_id(extract_field: Path, yaml_path: Path) -> str | None:
    """Return session.id from a YAML header, or None if unparseable/missing."""
    rc, out, _err = run([sys.executable, str(extract_field), "--file", str(yaml_path),
                         "--key", "session.id", "--doc-index", "0"])
    return out if rc == 0 and out else None


def pending_marker(sdir: Path, ttl_seconds: int) -> Path | None:
    """Return the newest in-flight turn marker of an ACTIVE session dir, or None.

    The logger writes `NNN-pending-*.yaml` into a session directory while one
    of its turns is executing — the strongest "this is the current session"
    signal. Markers older than `ttl_seconds` are treated as stale (crashed or
    force-quit turn); pass 0 to disable the TTL.
    """
    newest: Path | None = None
    for marker in sdir.glob("*-pending-*.yaml"):
        if newest is None or marker.stat().st_mtime > newest.stat().st_mtime:
            newest = marker
    if newest is None:
        return None
    if ttl_seconds > 0 and (time.time() - newest.stat().st_mtime) > ttl_seconds:
        return None
    return newest


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else find_repo_root()
    sort_by_mtime, extract_field = resolve_base_scripts(repo_root)
    if args.log_dir:
        log_dir = Path(args.log_dir).expanduser().resolve()
    elif os.environ.get(ENV_LOG_DIR_VAR, "").strip():
        log_dir = Path(os.environ[ENV_LOG_DIR_VAR]).expanduser().resolve()
    else:
        log_dir = repo_root / ".opencode/logs"

    # Dry-run: print discovery info and exit
    if args.dry_run:
        print(json.dumps({
            "repo_root": str(repo_root),
            "log_dir": str(log_dir),
            "sort_by_mtime": str(sort_by_mtime),
            "extract_field": str(extract_field),
            "since": args.since,
        }, ensure_ascii=False))
        return 0

    if not sort_by_mtime.is_file():
        print(f"ERROR: sort-by-mtime.py not found at {sort_by_mtime}", file=sys.stderr)
        return 1
    if not extract_field.is_file():
        print(f"ERROR: extract-field.py not found at {extract_field}", file=sys.stderr)
        return 1
    if not log_dir.is_dir():
        print(f"ERROR: .opencode/logs not found at {log_dir}", file=sys.stderr)
        return 1

    # Fast path: order ses_*/ dirs pending-marker-first (an in-flight turn
    # writes `NNN-pending-*.yaml` into the ACTIVE session's dir — the
    # strongest "this is the current session" signal), then newest-mtime.
    # Accept the first header in that order whose session.id actually parses:
    # a corrupt newest header must not shadow an older healthy session.
    session_dirs = [d for d in log_dir.iterdir() if d.is_dir() and d.name.startswith("ses_")]

    # Apply --since filter if provided
    if args.since:
        try:
            since_ts = datetime.fromisoformat(args.since).timestamp()
            session_dirs = [d for d in session_dirs if d.stat().st_mtime >= since_ts]
        except ValueError:
            print(f"ERROR: --since requires valid ISO timestamp (e.g. 2026-09-19T10:00:00)", file=sys.stderr)
            return 1

    pending_map = {d: pending_marker(d, args.pending_ttl) for d in session_dirs}
    pending_dirs = [d for d in session_dirs if pending_map[d] is not None]
    session_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    if pending_dirs:
        pending_dirs.sort(key=lambda d: pending_map[d].stat().st_mtime, reverse=True)
        if len(pending_dirs) > 1:
            names = ", ".join(d.name for d in pending_dirs)
            print(f"WARNING: multiple sessions have in-flight turns ({names}); "
                  f"selecting the newest pending session", file=sys.stderr)
        session_dirs = pending_dirs + [d for d in session_dirs if d not in pending_dirs]

    # Probe top-N dirs in parallel (default top 5), then pick the winner in
    # newest-first order — NOT completion order: a faster subprocess for an
    # older session must never beat the true newest session under load.
    yaml_path = None
    fast_sid: str | None = None
    max_parallel = 5
    candidates: list[tuple[Path, Path]] = []
    for sdir in session_dirs[:max_parallel]:
        header_files = sorted(sdir.glob("000-header-*.yaml"))
        if header_files:
            candidates.append((sdir, header_files[-1]))
    if candidates:
        with ThreadPoolExecutor(max_workers=min(max_parallel, len(candidates))) as executor:
            probes = list(executor.map(
                lambda cand: probe_session_id(extract_field, cand[1]), candidates))
        for (_, header), sid_probe in zip(candidates, probes):
            if sid_probe:
                yaml_path, fast_sid = header, sid_probe
                break

    # Fall back to flat *.yaml in log dir
    sort_err = ""
    if not yaml_path:
        rc, newest, sort_err = run([sys.executable, str(sort_by_mtime), "--dir", str(log_dir), "--glob", "*.yaml", "--limit", "1"])
        if rc == 0 and newest:
            try:
                newest_entry = json.loads(newest.splitlines()[0])
                yaml_path = log_dir / newest_entry["path"]
            except (json.JSONDecodeError, KeyError, IndexError):
                pass

    if not yaml_path:
        detail = f" (sort: {sort_err})" if sort_err else ""
        print(f"ERROR: could not find newest YAML log{detail}", file=sys.stderr)
        return 1

    if fast_sid is not None:
        sid, sid_err = fast_sid, ""
    else:
        rc, sid, sid_err = run([sys.executable, str(extract_field), "--file", str(yaml_path), "--key", "session.id", "--doc-index", "0"])
        if rc != 0 or not sid:
            detail = f" (extract-field: {sid_err})" if sid_err else ""
            print(f"ERROR: session.id not found in YAML header {yaml_path}{detail}", file=sys.stderr)
            return 1
    _rc, title, _err = run([sys.executable, str(extract_field), "--file", str(yaml_path), "--key", "title", "--doc-index", "0"])

    state_file = log_dir / f"{sid}.state.json"
    state_exists = state_file.is_file()
    title_val = title if title else None
    winner_pending = any(yaml_path.parent == d for d in pending_dirs)
    payload = {
        "session_id": sid,
        "title": title_val,
        "state": "exists" if state_exists else "missing",
        "pending": winner_pending,
        "yaml_path": str(yaml_path),
        "log_dir": str(log_dir),
    }

    gate_ok = args.state == "any" or (args.state == "exists") == state_exists
    if not gate_ok:
        if args.json:
            print(json.dumps(payload, ensure_ascii=False))
        else:
            print(f"ERROR: state-file gate not satisfied: required '{args.state}', "
                  f"found '{payload['state']}' for {sid}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
        return 0

    print(f"Session ID: {sid}")
    if title_val:
        print(f"Title: {title_val}")
    print(f"State file: {'exists' if state_exists else 'missing'}")
    print(f"Pending marker: {'yes' if winner_pending else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())