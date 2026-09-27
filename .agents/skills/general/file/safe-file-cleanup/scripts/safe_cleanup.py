#!/usr/bin/env python3
"""safe_cleanup.py — Generic safe file/directory removal primitive.

Tier 1 (Python 3.12+, stdlib only).
Uses the system trash/recycle bin when available; falls back to rm when not.
Outputs JSON Lines; exit codes: 0 = all removed, 1 = partial, 2 = all failed.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys


def find_trash_command():
    """Return the first available trash/recycle-bin CLI, or None."""
    candidates = ["trash", "gio", "recycle-bin"]
    for cmd in candidates:
        if shutil.which(cmd):
            return cmd
    return None


def remove_path(path, trash_cmd=None):
    """Remove a single file or directory. Returns (ok, message)."""
    if trash_cmd == "trash":
        proc = subprocess.run(["trash", path], capture_output=True, text=True)
        if proc.returncode == 0:
            return True, "moved to trash via `trash`"
        return False, f"`trash` failed: {proc.stderr.strip()}"
    elif trash_cmd == "gio":
        proc = subprocess.run(["gio", "trash", path], capture_output=True, text=True)
        if proc.returncode == 0:
            return True, "moved to trash via `gio trash`"
        return False, f"`gio trash` failed: {proc.stderr.strip()}"
    else:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True, "removed via stdlib fallback (no trash command found)"


def verify_removed(path):
    return not os.path.exists(path)


def remove_empty_parents(paths):
    """Remove empty parent directories up to the nearest non-empty ancestor."""
    for path in paths:
        if os.path.exists(path):
            continue
        parent = os.path.dirname(path)
        while parent and parent != os.path.dirname(parent):
            try:
                if os.path.isdir(parent) and not os.listdir(parent):
                    os.rmdir(parent)
                    parent = os.path.dirname(parent)
                else:
                    break
            except OSError:
                break


def main():
    parser = argparse.ArgumentParser(
        description="Safely remove files/directories, preferring the system trash."
    )
    parser.add_argument("paths", nargs="+", help="Files or directories to remove")
    parser.add_argument(
        "--remove-empty-parents",
        action="store_true",
        help="Remove empty parent directories after successful deletions",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON Lines output",
    )
    args = parser.parse_args()

    trash_cmd = find_trash_command()
    results = []
    all_ok = True
    any_ok = False
    success_paths = []

    for path in args.paths:
        if not os.path.exists(path):
            results.append(
                {"path": path, "status": "skipped", "message": "does not exist"}
            )
            continue

        ok, msg = remove_path(path, trash_cmd)
        if ok and verify_removed(path):
            results.append({"path": path, "status": "removed", "message": msg})
            any_ok = True
            success_paths.append(path)
        else:
            results.append({"path": path, "status": "failed", "message": msg})
            all_ok = False

    if args.remove_empty_parents and success_paths:
        remove_empty_parents(success_paths)

    for r in results:
        if args.json:
            print(json.dumps(r))
        else:
            print(f"{r['status']}: {r['path']} — {r['message']}")

    if all_ok:
        sys.exit(0)
    elif any_ok:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
