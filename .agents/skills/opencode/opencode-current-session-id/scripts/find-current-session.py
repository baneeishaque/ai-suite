#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[4]  # ../../../../ from scripts/

SORT_BY_MTIME = REPO_ROOT / ".agents/skills/general/file/file-glob-sort-by-mtime/scripts/sort-by-mtime.py"
EXTRACT_FIELD = REPO_ROOT / ".agents/skills/general/yaml-field-extract/scripts/extract-field.py"
LOG_DIR = REPO_ROOT / ".opencode/logs"


def run(args: list[str]) -> tuple[int, str]:
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip()
    except FileNotFoundError as exc:
        return 127, f"File not found: {exc.filename}"
    except subprocess.TimeoutExpired:
        return 124, "Timed out"


def main() -> int:
    if not SORT_BY_MTIME.is_file():
        print(f"ERROR: sort-by-mtime.py not found at {SORT_BY_MTIME}", file=sys.stderr)
        return 1
    if not EXTRACT_FIELD.is_file():
        print(f"ERROR: extract-field.py not found at {EXTRACT_FIELD}", file=sys.stderr)
        return 1
    if not LOG_DIR.is_dir():
        print(f"ERROR: .opencode/logs not found at {LOG_DIR}", file=sys.stderr)
        return 1

    # Try flat-timestamped format: session subdirs with 000-header-*.yaml
    session_dirs = sorted([d for d in LOG_DIR.iterdir() if d.is_dir() and d.name.startswith("ses_")],
                          key=lambda d: d.stat().st_mtime, reverse=True)
    yaml_path = None
    if session_dirs:
        header_files = sorted(session_dirs[0].glob("000-header-*.yaml"))
        if header_files:
            yaml_path = header_files[-1]

    # Fall back to flat *.yaml in log dir
    if not yaml_path:
        rc, newest = run([sys.executable, str(SORT_BY_MTIME), "--dir", str(LOG_DIR), "--glob", "*.yaml", "--limit", "1"])
        if rc == 0 and newest:
            try:
                newest_entry = json.loads(newest.splitlines()[0])
                yaml_path = LOG_DIR / newest_entry["path"]
            except (json.JSONDecodeError, KeyError, IndexError):
                pass

    if not yaml_path:
        print("ERROR: could not find newest YAML log", file=sys.stderr)
        return 1

    rc, sid = run([sys.executable, str(EXTRACT_FIELD), "--file", str(yaml_path), "--key", "session.id", "--doc-index", "0"])
    rc2, title = run([sys.executable, str(EXTRACT_FIELD), "--file", str(yaml_path), "--key", "title", "--doc-index", "0"])

    if rc != 0:
        print("ERROR: session.id not found in YAML header", file=sys.stderr)
        return 1

    state_file = LOG_DIR / f"{sid}.state.json"
    state_exists = state_file.is_file()

    print(f"Session ID: {sid}")
    if rc2 == 0 and title:
        print(f"Title: {title}")
    print(f"State file: {'exists' if state_exists else 'missing'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
