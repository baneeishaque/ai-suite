#!/usr/bin/env python3
"""
json-diff-cli — Human-readable JSON leaf diff.

Calls the json-diff-leaf base primitive for the structured diff, then enriches
the output with timestamp formatting, set-based list-item presentation, and a
summary conclusion.

Usage:
  python3 json-diff-cli.py <file1> <file2>
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _resolve_base_script() -> Path:
    script_dir = Path(__file__).resolve().parent
    base = script_dir / ".." / ".." / "json-diff-leaf" / "scripts" / "json-diff-leaf.py"
    if not base.exists():
        print(f"Error: base script not found at {base}", file=sys.stderr)
        sys.exit(1)
    return base


def _fmt_ts(val: Any) -> str:
    if not isinstance(val, (int, float)):
        return json.dumps(val)
    if val > 1e11:
        dt = datetime.fromtimestamp(val / 1000, tz=timezone.utc)
        return f"{json.dumps(val)} ({dt.strftime('%Y-%m-%d %H:%M:%S UTC')})"
    return json.dumps(val)


def _format_list(val: list) -> str:
    if not val:
        return "[]"
    if all(isinstance(v, str) for v in val):
        return "\n    " + "\n    ".join(f"- {v}" for v in sorted(val))
    return json.dumps(val, indent=2)


def _is_timestamp_path(path: str) -> bool:
    last = path.rsplit(".", 1)[-1].lower()
    return "last-update" in last or "timestamp" in last or "time" in last


def _conclusion(changes: list[dict], name1: str, name2: str) -> str:
    if not changes:
        return "Files are identical."

    added = [c for c in changes if c["kind"] == "added"]
    removed = [c for c in changes if c["kind"] == "removed"]
    changed = [c for c in changes if c["kind"] == "changed"]
    reordered = [c for c in changes if c["kind"] == "reordered"]

    parts = []
    if added:
        keys = ", ".join(c["path"] for c in added)
        parts.append(f"{len(added)} key(s) added ({keys})")
    if removed:
        keys = ", ".join(c["path"] for c in removed)
        parts.append(f"{len(removed)} key(s) removed ({keys})")
    if changed:
        keys = ", ".join(c["path"] for c in changed)
        parts.append(f"{len(changed)} value(s) changed ({keys})")
    if reordered:
        keys = ", ".join(c["path"] for c in reordered)
        parts.append(f"{len(reordered)} array(s) reordered ({keys})")

    summary = f"{name2} has " + "; ".join(parts) + "."

    if added and not removed:
        summary += f" {name2} is a superset of {name1}."
    elif removed and not added:
        summary += f" {name2} is a subset of {name1}."

    for c in changes:
        if c["kind"] == "changed" and _is_timestamp_path(c["path"]):
            o, n = c["old_value"], c["new_value"]
            if isinstance(o, (int, float)) and isinstance(n, (int, float)):
                older, newer = (o, n) if o < n else (n, o)
                newer_name = name2 if n > o else name1
                summary += f" ({c['path']}: {newer_name} is newer — {_fmt_ts(newer)} > {_fmt_ts(older)})"

    return summary


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <file1> <file2>", file=sys.stderr)
        sys.exit(1)

    file1, file2 = Path(sys.argv[1]), Path(sys.argv[2])
    base_script = _resolve_base_script()

    result = subprocess.run(
        [sys.executable, str(base_script), "--file1", str(file1), "--file2", str(file2)],
        capture_output=True, text=True, check=True,
    )

    changes: list[dict] = json.loads(result.stdout)

    if not changes:
        print("Files are identical.")
        sys.exit(0)

    name1, name2 = file1.name, file2.name

    for c in changes:
        path, kind = c["path"], c["kind"]
        label = {
            "added": "ADDED",
            "removed": "REMOVED",
            "changed": "CHANGED",
            "reordered": "REORDERED",
            "type-changed": "TYPE-CHANGED",
        }.get(kind, kind)
        print(f"{label}  {path}")

        if kind in ("added",):
            val = c.get("new_value")
            if isinstance(val, list):
                print(f"  [{name2}] added items:{_format_list(val)}")
            else:
                print(f"  [{name2}] value: {_fmt_ts(val)}")
        elif kind in ("removed",):
            val = c.get("old_value")
            if isinstance(val, list):
                print(f"  [{name1}] removed items:{_format_list(val)}")
            else:
                print(f"  [{name1}] value: {_fmt_ts(val)}")
        elif kind == "changed":
            print(f"  [{name1}] {_fmt_ts(c['old_value'])}")
            print(f"  [{name2}] {_fmt_ts(c['new_value'])}")
        elif kind == "reordered":
            print(f"  [{name1}] {json.dumps(c['old_value'])}")
            print(f"  [{name2}] {json.dumps(c['new_value'])}")
        elif kind == "type-changed":
            print(f"  [{name1}] {c['old_value']}")
            print(f"  [{name2}] {c['new_value']}")
        print()

    print("─── CONCLUSION ───")
    print(_conclusion(changes, name1, name2))


if __name__ == "__main__":
    main()
