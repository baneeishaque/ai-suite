#!/usr/bin/env python3
"""
json-content-compare-ignore-keys.py

Compare JSON file content while ignoring specified keys.
First run: stores snapshot of (sorted, filtered) JSON.
Subsequent runs: compare current against snapshot.
Exit 0 = MATCH, Exit 1 = MISMATCH.

Tier: 1 (Python 3.12+)
Rationale: JSON parsing + key filtering + hashing is Python's native
strength. Bash regex-on-JSON would be fragile. See
scripting-language-selection-rules.md section 3.1.
"""

import argparse
import hashlib
import json
import pathlib
import sys


def parse_args():
    p = argparse.ArgumentParser(
        description="Compare JSON file content while ignoring specified keys."
    )
    p.add_argument("--file", required=True, type=pathlib.Path,
                    help="JSON file to compare")
    p.add_argument("--ignore-keys", action="append", default=[],
                    help="Key(s) to remove before hashing (repeatable)")
    p.add_argument("--snapshot-dir", type=pathlib.Path, default=None,
                    help="Where to store/read snapshot files (default: same "
                         "directory as --file)")
    return p.parse_args()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def strip_keys(obj, keys_to_ignore):
    """Return a new dict/list with specified keys removed (recursive)."""
    if isinstance(obj, dict):
        return {
            k: strip_keys(v, keys_to_ignore)
            for k, v in obj.items()
            if k not in keys_to_ignore
        }
    if isinstance(obj, list):
        return [strip_keys(item, keys_to_ignore) for item in obj]
    return obj


def canonical_hash(obj):
    """Deterministic hash of JSON (sorted keys, compact, UTF-8)."""
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False,
                     separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def main():
    args = parse_args()
    snap_dir = args.snapshot_dir or args.file.parent
    snap_path = snap_dir / f"{args.file.name}.snapshot"

    if not args.file.exists():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    data = load_json(args.file)
    filtered = strip_keys(data, set(args.ignore_keys))
    current_hash = canonical_hash(filtered)

    if not snap_path.exists():
        snap_path.write_text(current_hash + "\n", encoding="utf-8")
        print(f"[json-compare] Snapshot created: {snap_path}")
        sys.exit(0)

    stored_hash = snap_path.read_text(encoding="utf-8").strip()
    if current_hash == stored_hash:
        print(f"[json-compare] MATCH: {args.file.name}")
        sys.exit(0)
    else:
        print(f"[json-compare] MISMATCH: {args.file.name}")
        sys.exit(1)


if __name__ == "__main__":
    main()
