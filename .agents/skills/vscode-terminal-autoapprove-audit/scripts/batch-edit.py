#!/usr/bin/env python3
"""
batch-edit.py — Apply many add/replace/delete operations to autoApprove in one pass.

Part of the vscode-terminal-autoapprove-audit skill.
Companion to edit-entry.py — solves two operational problems:

  1. Spawning edit-entry.py N times is N × Python startup cost.
  2. On Windows PowerShell, regex keys containing backticks, '$', or inner
     quotes get mangled when passed as --key arguments. Reading keys from a
     JSONL file sidesteps all shell quoting.

Operation file format — JSON Lines, one op per line:

    {"op": "add",         "key": "/^…$/"}
    {"op": "add",         "key": "/^…$/", "matchCommandLine": false}
    {"op": "replace",     "old": "loose-prefix", "new": "/^anchored$/"}
    {"op": "replace",     "old": "/^a$/", "new": "/^b$/", "matchCommandLine": false}
    {"op": "update",      "key": "/^…$/", "matchCommandLine": false}
    {"op": "delete",      "key": "exact-key"}
    {"op": "delete-grep", "key": "unique-substring"}

`add`/`replace` default to `{approve: true, matchCommandLine: true}` unless
`matchCommandLine` is given. `update` mutates only the value of an existing
entry (key position preserved); at least one of `approve` / `matchCommandLine`
must be supplied.

Comments: lines starting with '#' and blank lines are ignored.

Usage:
    python3 batch-edit.py --settings <path> --ops <ops.jsonl>
    python3 batch-edit.py --settings <path> --ops - < ops.jsonl   # stdin

Run fix-indents.py afterwards (SKILL.md §3.1).

Exit codes:
    0  all ops succeeded     1  one or more ops failed (file unchanged)
"""

import argparse
import collections
import json
import sys


_APPROVE = {"approve": True, "matchCommandLine": True}


def _value(op: dict) -> dict:
    """Build the value dict for an add/replace op, applying overrides."""
    v = dict(_APPROVE)
    if "approve" in op:
        v["approve"] = bool(op["approve"])
    if "matchCommandLine" in op:
        v["matchCommandLine"] = bool(op["matchCommandLine"])
    return v


def _load(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=collections.OrderedDict)


def _save(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def _read_ops(src: str) -> list[dict]:
    # 'utf-8-sig' silently strips a BOM if present (PowerShell 5 `Out-File -Encoding utf8`).
    fp = sys.stdin if src == "-" else open(src, encoding="utf-8-sig")
    try:
        ops = []
        for lineno, raw in enumerate(fp, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                ops.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SystemExit(f"ERROR: ops:{lineno} invalid JSON: {e}")
        return ops
    finally:
        if fp is not sys.stdin:
            fp.close()


def _apply(aa, op: dict) -> tuple[bool, str]:
    """Returns (ok, message). aa is the OrderedDict; mutated in place on ok."""
    kind = op.get("op")
    if kind == "add":
        k = op.get("key")
        if not k:
            return False, "add: missing 'key'"
        if k in aa:
            return False, f"add: key already present: {k[:80]!r}"
        aa[k] = _value(op)
        return True, f"add: {k[:80]!r}"

    if kind == "replace":
        old, new = op.get("old"), op.get("new")
        if not (old and new):
            return False, "replace: requires 'old' and 'new'"
        if old not in aa:
            return False, f"replace: old not found: {old[:80]!r}"
        if new != old and new in aa:
            return False, f"replace: new key collides: {new[:80]!r}"
        # Preserve position.
        rebuilt = collections.OrderedDict()
        for k, v in aa.items():
            if k == old:
                rebuilt[new] = _value(op)
            else:
                rebuilt[k] = v
        aa.clear(); aa.update(rebuilt)
        return True, f"replace: {old[:50]!r} -> {new[:50]!r}"

    if kind == "update":
        k = op.get("key")
        if not k:
            return False, "update: missing 'key'"
        if k not in aa:
            return False, f"update: key not found: {k[:80]!r}"
        if "approve" not in op and "matchCommandLine" not in op:
            return False, "update: supply 'approve' and/or 'matchCommandLine'"
        # Preserve any existing flags not overridden.
        existing = aa[k] if isinstance(aa[k], dict) else dict(_APPROVE)
        merged = dict(existing)
        if "approve" in op:
            merged["approve"] = bool(op["approve"])
        if "matchCommandLine" in op:
            merged["matchCommandLine"] = bool(op["matchCommandLine"])
        aa[k] = merged
        return True, f"update: {k[:60]!r} -> {merged}"

    if kind == "delete":
        k = op.get("key")
        if not k:
            return False, "delete: missing 'key'"
        if k not in aa:
            return False, f"delete: key not found: {k[:80]!r}"
        del aa[k]
        return True, f"delete: {k[:80]!r}"

    if kind == "delete-grep":
        sub = op.get("key")
        if not sub:
            return False, "delete-grep: missing 'key' (substring)"
        hits = [k for k in aa if sub in k]
        if len(hits) != 1:
            return False, f"delete-grep: {len(hits)} matches for {sub[:60]!r} (want exactly 1)"
        del aa[hits[0]]
        return True, f"delete-grep: {hits[0][:80]!r}"

    return False, f"unknown op: {kind!r}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Batch edit autoApprove entries.")
    ap.add_argument("--settings", required=True)
    ap.add_argument("--ops", required=True, help="Path to JSONL ops file (- for stdin)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Validate every op against a working copy without writing")
    args = ap.parse_args()

    data = _load(args.settings)
    aa = data.setdefault("chat.tools.terminal.autoApprove", collections.OrderedDict())
    before = len(aa)

    ops = _read_ops(args.ops)
    if not ops:
        print("No operations to apply.", file=sys.stderr)
        return 0

    failures = []
    for i, op in enumerate(ops, 1):
        ok, msg = _apply(aa, op)
        marker = "OK  " if ok else "FAIL"
        print(f"[{i:03}] {marker} {msg}")
        if not ok:
            failures.append((i, msg))

    if failures:
        print(f"\n{len(failures)} op(s) failed — file NOT written.", file=sys.stderr)
        return 1

    after = len(aa)
    if args.dry_run:
        print(f"\nDry-run OK. Would write: {before} -> {after} entries.")
        return 0

    _save(args.settings, data)
    print(f"\nWrote {args.settings}. entries: {before} -> {after}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
