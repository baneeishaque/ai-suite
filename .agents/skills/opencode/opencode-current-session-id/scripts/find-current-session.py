#!/usr/bin/env python3
"""Discover the current opencode session ID from logger logs.

Composer: sequences file-glob-sort-by-mtime + yaml-field-extract base skills.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

ENV_REPO_ROOT_VARS = ("OPENCODE_REPO_ROOT", "AI_SUITE_ROOT")
ENV_LOG_DIR_VAR = "OPENCODE_LOGS_DIR"


def find_repo_root(start: Path = SCRIPT_DIR) -> Path:
    """Resolve repo root via env override, git top-level, legacy fallback."""
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
    return ap.parse_args(argv)


def run(args: list[str]) -> tuple[int, str]:
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip()
    except FileNotFoundError as exc:
        return 127, f"File not found: {exc.filename}"
    except subprocess.TimeoutExpired:
        return 124, "Timed out"


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

    if not sort_by_mtime.is_file():
        print(f"ERROR: sort-by-mtime.py not found at {sort_by_mtime}", file=sys.stderr)
        return 1
    if not extract_field.is_file():
        print(f"ERROR: extract-field.py not found at {extract_field}", file=sys.stderr)
        return 1
    if not log_dir.is_dir():
        print(f"ERROR: .opencode/logs not found at {log_dir}", file=sys.stderr)
        return 1

    # Try flat-timestamped format: session subdirs with 000-header-*.yaml
    session_dirs = sorted([d for d in log_dir.iterdir() if d.is_dir() and d.name.startswith("ses_")],
                          key=lambda d: d.stat().st_mtime, reverse=True)
    yaml_path = None
    if session_dirs:
        header_files = sorted(session_dirs[0].glob("000-header-*.yaml"))
        if header_files:
            yaml_path = header_files[-1]

    # Fall back to flat *.yaml in log dir
    if not yaml_path:
        rc, newest = run([sys.executable, str(sort_by_mtime), "--dir", str(log_dir), "--glob", "*.yaml", "--limit", "1"])
        if rc == 0 and newest:
            try:
                newest_entry = json.loads(newest.splitlines()[0])
                yaml_path = log_dir / newest_entry["path"]
            except (json.JSONDecodeError, KeyError, IndexError):
                pass

    if not yaml_path:
        print("ERROR: could not find newest YAML log", file=sys.stderr)
        return 1

    rc, sid = run([sys.executable, str(extract_field), "--file", str(yaml_path), "--key", "session.id", "--doc-index", "0"])
    rc2, title = run([sys.executable, str(extract_field), "--file", str(yaml_path), "--key", "title", "--doc-index", "0"])

    if rc != 0 or not sid:
        print("ERROR: session.id not found in YAML header", file=sys.stderr)
        return 1

    state_file = log_dir / f"{sid}.state.json"
    state_exists = state_file.is_file()
    title_val = title if (rc2 == 0 and title) else None

    if args.json:
        print(json.dumps({
            "session_id": sid,
            "title": title_val,
            "state": "exists" if state_exists else "missing",
            "yaml_path": str(yaml_path),
            "log_dir": str(log_dir),
        }, ensure_ascii=False))
        return 0

    print(f"Session ID: {sid}")
    if title_val:
        print(f"Title: {title_val}")
    print(f"State file: {'exists' if state_exists else 'missing'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
