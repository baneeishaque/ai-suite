#!/usr/bin/env python3
from __future__ import annotations
import argparse, glob, json, os, sys
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser(description="List files matching glob sorted by mtime descending (JSON Lines)")
    ap.add_argument("--dir", required=True, help="Directory to search")
    ap.add_argument("--glob", required=True, help="Glob pattern (e.g. *.yaml)")
    ap.add_argument("--limit", type=int, default=0, help="Max results (0 = unlimited)")
    args = ap.parse_args()

    root = Path(args.dir).resolve()
    if not root.is_dir():
        print(f"ERROR: directory not found: {root}", file=sys.stderr)
        return 1

    entries = []
    for p in sorted(root.rglob(args.glob)):
        try:
            st = p.stat()
            entries.append({"path": str(p.relative_to(root)), "mtime": int(st.st_mtime_ns), "size": st.st_size})
        except OSError:
            continue

    entries.sort(key=lambda e: e["mtime"], reverse=True)

    if args.limit > 0:
        entries = entries[: args.limit]

    for e in entries:
        print(json.dumps(e, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
