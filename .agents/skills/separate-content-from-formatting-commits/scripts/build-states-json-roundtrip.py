#!/usr/bin/env python3
"""JSON round-trip intermediate-state builder (reformat-aware).

Use ONLY when the user intentionally wants one commit that reformats the
file, with subsequent commits adding semantic changes on top of the new
format.  Every output state carries the NEW format because JSON is
fully re-serialized on each write.

If the user wants the reformat as a SEPARATE trailing commit (content
commits first, format commit last), use build-states-textual.py instead.

Mutations file (JSON) schema — each top-level element covers one commit:
  [
    [
      {"op": "rename_key", "parent_path": ["hooks"], "from": "OldKey", "to": "NewKey"},
      {"op": "set",        "parent_path": ["model"], "key": "name", "value": "new-model"}
    ],
    [
      {"op": "delete", "parent_path": ["deprecated"], "key": "legacyFlag"}
    ]
  ]

Ops:
  set        - sets obj[path][key] = value
  delete     - deletes obj[path][key]
  rename_key - renames a key inside obj[path] preserving insertion order

--indent: 'tab' (default) or an integer number of spaces.
"""
import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path


def get_at(obj, path):
    for key in path:
        obj = obj[key]
    return obj


def apply_op(root, op):
    kind   = op["op"]
    parent = get_at(root, op.get("parent_path", []))
    if kind == "set":
        parent[op["key"]] = op["value"]
    elif kind == "delete":
        del parent[op["key"]]
    elif kind == "rename_key":
        new_parent = OrderedDict()
        for k, v in parent.items():
            new_parent[op["to"] if k == op["from"] else k] = v
        parent.clear()
        parent.update(new_parent)
    else:
        raise ValueError(f"unknown op: {kind!r}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--baseline",  required=True)
    p.add_argument("--mutations", required=True, help="ordered list of mutation groups (JSON file)")
    p.add_argument("--out-dir",   required=True)
    p.add_argument("--indent",    default="tab", help="'tab' or integer spaces (default: tab)")
    p.add_argument("--target",    help="optional: final state must JSON-equal this file")
    args = p.parse_args()

    indent = "\t" if args.indent == "tab" else int(args.indent)

    baseline_text = Path(args.baseline).read_text(encoding="utf-8")
    obj           = json.loads(baseline_text, object_pairs_hook=OrderedDict)
    groups        = json.loads(Path(args.mutations).read_text(encoding="utf-8"))
    out_dir       = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Sanity: round-trip must preserve semantics before any mutations
    rt = json.dumps(obj, indent=indent, ensure_ascii=False) + "\n"
    if json.loads(rt) != json.loads(baseline_text):
        print("[FAIL] baseline round-trip lost semantic equality", file=sys.stderr)
        return 2
    print("[ok] baseline round-trip is semantically equal")

    for i, group in enumerate(groups, start=1):
        ops = group if isinstance(group, list) else [group]
        for op in ops:
            apply_op(obj, op)
        text = json.dumps(obj, indent=indent, ensure_ascii=False) + "\n"
        out  = out_dir / f"state-{i}.out"
        out.write_text(text, encoding="utf-8")
        print(f"[ok] wrote {out}  ({len(text)} bytes)")

    if args.target:
        if json.loads(Path(args.target).read_text(encoding="utf-8")) != obj:
            print("[FAIL] final state does not JSON-equal --target", file=sys.stderr)
            return 2
        print("[ok] final state JSON-equals --target")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
