#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML"]
# ///
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install: pip install PyYAML", file=sys.stderr)
    sys.exit(2)


def dot_get(d: dict, path: str):
    parts = path.split(".")
    cur: object = d
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract a field from a YAML file by dot-separated key path")
    ap.add_argument("--file", required=True, help="Path to YAML file")
    ap.add_argument("--key", required=True, help="Dot-separated key path (e.g. session.id)")
    ap.add_argument("--doc-index", type=int, default=0, help="Document index for multi-doc YAML (default: 0)")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"ERROR: could not read {path}: {exc}", file=sys.stderr)
        return 1

    docs = list(yaml.safe_load_all(text))
    if not docs:
        print("ERROR: empty YAML document", file=sys.stderr)
        return 1
    if args.doc_index >= len(docs):
        print(f"ERROR: doc-index {args.doc_index} out of range (0-{len(docs)-1})", file=sys.stderr)
        return 1

    value = dot_get(docs[args.doc_index], args.key)
    if value is None:
        return 1

    if isinstance(value, (dict, list)):
        print(json.dumps(value, ensure_ascii=False))
    else:
        print(str(value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
