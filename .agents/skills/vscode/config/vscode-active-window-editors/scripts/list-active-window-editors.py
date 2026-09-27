#!/usr/bin/env python3
"""Discover the active VS Code window's state.vscdb on macOS and list its
open editors by delegating to the vscode-state-vscdb-editor-extract base skill.

Workflow:
  1. Resolve the Code-family app data directory
     (~/Library/Application Support/<app>/User/workspaceStorage/).
  2. Sort workspaceStorage/* entries by mtime descending — the newest entry
     is the active window.
  3. Read workspace.json to identify the workspace folder (for cross-check).
  4. Resolve <entry>/state.vscdb.
  5. Delegate to extract-editors.py via anchored relative path.

This is the macOS-specific discovery layer. The OS-agnostic parsing of
state.vscdb → editor paths + pinned annotation lives in the base skill
vscode-state-vscdb-editor-extract (scripts/extract-editors.py).

Tier 1 (Python 3.12+, stdlib only) per scripting-language-selection-rules §2.1.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_SCRIPT = os.path.join(
    SCRIPT_DIR,
    "..",
    "..",
    "vscode-state-vscdb-editor-extract",
    "scripts",
    "extract-editors.py",
)

# VS Code app names on macOS, tried in priority order.
CODE_APP_NAMES = [
    "Code - Insiders",
    "Code",
    "VSCodium",
    "Cursor",
    "Code - Insiders Beta",
    "Code - Exploration",
]


def resolve_workspace_storage(app_name: str) -> str | None:
    """Resolve the workspaceStorage directory for a given Code-family app.

    Returns the absolute path if it exists, or None.
    """
    home = os.path.expanduser("~")
    base = os.path.join(
        home, "Library", "Application Support", app_name, "User", "workspaceStorage"
    )
    if os.path.isdir(base):
        return base
    return None


def find_active_workspace_dir(storage_base: str) -> tuple[str | None, dict | None]:
    """Find the most-recently-modified workspaceStorage entry (active window).

    Returns (dir_path, workspace_json_dict). If workspace.json is absent,
    returns (dir_path, None).
    """
    entries = sorted(
        Path(storage_base).iterdir(),
        key=lambda p: p.stat().st_mtime_ns,
        reverse=True,
    )
    for entry in entries:
        db_candidate = entry / "state.vscdb"
        if db_candidate.is_file():
            wj = entry / "workspace.json"
            info: dict | None = None
            if wj.is_file():
                try:
                    info = json.loads(wj.read_text())
                except (json.JSONDecodeError, OSError):
                    info = None
            return str(entry), info
    return None, None


def discover_db_path(app_name: str | None) -> tuple[str, str, dict | None]:
    """Discover the active window's state.vscdb path.

    Returns (app_name, db_path, workspace_info).
    Exits with code 2 if no Code-family app is found.
    """
    apps_to_try = [app_name] if app_name else CODE_APP_NAMES
    for name in apps_to_try:
        storage = resolve_workspace_storage(name)
        if storage is None:
            sys.stderr.write(f"NOTE: no workspaceStorage for app '{name}'\n")
            continue
        entry_dir, info = find_active_workspace_dir(storage)
        if entry_dir is None:
            sys.stderr.write(f"WARNING: {name} has no state.vscdb entries\n")
            continue
        db_path = os.path.join(entry_dir, "state.vscdb")
        return name, db_path, info
    sys.stderr.write(
        "ERROR: no Code-family app found with a workspaceStorage/state.vscdb.\n"
        "       Tried: " + ", ".join(apps_to_try) + "\n"
    )
    sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List open VS Code editor tabs (active window) via "
                    "state.vscdb, delegating parsing to the base skill"
    )
    parser.add_argument(
        "--app", default=None,
        help="Code-family app name (default: auto-detect; "
             f"tries {', '.join(CODE_APP_NAMES)})",
    )
    parser.add_argument(
        "--db", default=None,
        help="Override: use a specific state.vscdb path (skip discovery)",
    )
    parser.add_argument("--json", action="store_true",
                        help="Pass --json to the base extractor for "
                             "machine-readable output")
    parser.add_argument(
        "--mode", choices=["all", "files"], default="all",
        help="Pass --mode to the base extractor: 'all' = every tab "
             "(file/webview/terminal) with [type] tags and # group markers "
             "(default); 'files' = file-only projection",
    )
    args = parser.parse_args()

    # Verify base script exists
    base_resolved = os.path.realpath(BASE_SCRIPT)
    if not os.path.isfile(base_resolved):
        sys.stderr.write(
            f"ERROR: base script not found at {base_resolved}\n"
            f"       Ensure vscode-state-vscdb-editor-extract is installed "
            f"at the expected relative path.\n"
        )
        sys.exit(2)

    if args.db:
        db_path = os.path.abspath(args.db)
        app_name = "(explicit --db override)"
        info = None
    else:
        app_name, db_path, info = discover_db_path(args.app)

    # Print a header line (to stderr so stdout stays clean for piping)
    sys.stderr.write(f"App: {app_name}\n")
    sys.stderr.write(f"DB:  {db_path}\n")
    if info:
        folder = info.get("folder") or info.get("workspace")
        if folder:
            sys.stderr.write(f"Workspace: {folder}\n")

    # Delegate to base
    cmd = [sys.executable, base_resolved, "--db", db_path]
    if args.mode != "all":
        cmd.extend(["--mode", args.mode])
    if args.json:
        cmd.append("--json")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
