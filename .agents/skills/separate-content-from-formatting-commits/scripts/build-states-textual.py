#!/usr/bin/env python3
"""Format-preserving intermediate-state builder.

Given a baseline file and an ordered list of textual edits (each covering
one semantic change), writes N intermediate state files. State N is
produced by applying edits 1..N to the baseline as plain-text substring
replacements, so the file's original whitespace, key order, and indentation
are byte-preserved everywhere outside the patched span.

Use this when a working-tree diff mixes a reformat with several semantic
changes and the user wants every content commit to land on the ORIGINAL
format. The optional reformat commit comes last (see sibling script).

Edits file (JSON) schema:
  [
    {"kind": "replace",        "old": "...", "new": "..."},
    {"kind": "replace_unique", "old": "...", "new": "..."},
    {"kind": "append_before_suffix", "suffix": "...", "insert": "..."}
  ]

replace        - replaces ALL occurrences (assert at least one found)
replace_unique - asserts old appears EXACTLY once, then replaces
append_before_suffix - inserts `insert` immediately before the trailing
                       `suffix` (useful for appending a new top-level entry)

Output: writes state-1.out, state-2.out, ... into --out-dir.
Copy each onto the working-tree path before the corresponding git commit.
"""
import argparse
import json
import sys
from pathlib import Path


def apply_edit(text, edit):
    kind = edit["kind"]
    if kind == "replace":
        new = text.replace(edit["old"], edit["new"])
        assert new != text, f"replace produced no change: {edit['old'][:60]!r}"
        return new
    if kind == "replace_unique":
        count = text.count(edit["old"])
        assert count == 1, f"replace_unique: expected 1 match, found {count}: {edit['old'][:60]!r}"
        return text.replace(edit["old"], edit["new"], 1)
    if kind == "append_before_suffix":
        suffix = edit["suffix"]
        assert text.endswith(suffix), f"file does not end with suffix {suffix!r}"
        return text[: -len(suffix)] + edit["insert"] + suffix
    raise ValueError(f"unknown edit kind: {kind!r}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--baseline", required=True, help="path to baseline file (HEAD state)")
    p.add_argument("--edits",    required=True, help="path to JSON edits file (ordered list)")
    p.add_argument("--out-dir",  required=True, help="directory to write state-N.out files")
    p.add_argument("--target",   help="optional working-tree path; final state must match byte-for-byte")
    args = p.parse_args()

    baseline = Path(args.baseline).read_text(encoding="utf-8")
    edits    = json.loads(Path(args.edits).read_text(encoding="utf-8"))
    out_dir  = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    state = baseline
    for i, edit in enumerate(edits, start=1):
        state = apply_edit(state, edit)
        out = out_dir / f"state-{i}.out"
        out.write_text(state, encoding="utf-8")
        print(f"[ok] wrote {out}  ({len(state)} bytes)")

    if args.target:
        expected = Path(args.target).read_text(encoding="utf-8")
        if state != expected:
            print("[FAIL] final state does not match --target byte-for-byte", file=sys.stderr)
            return 2
        print("[ok] final state == --target  (byte-perfect)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
