#!/usr/bin/env python3
"""planning-superseded-version-retirement — composer executable half.

Retire a superseded version of a versioned planning artifact (v1 superseded by v2).

Owned by: .agents/skills/general/planning/planning-superseded-version-retirement/
Consumes:   ../planning-version-coverage-audit/scripts/audit-version-coverage.py   (coverage gate)
SSOT:       SKILL.md (prose gates live there, not here)

BEST PRACTICES: run with --dry-run FIRST; execute only with --confirm <token> where
<token> matches the exact slice of user authorization ("DELETE" is the canonical token).

Exit codes:
  0  OK: dry-run clean / retirement applied / verify clean
  1  Coverage not FULL, or STALE references remain after --verify
  2  Usage error
  3  Missing consent token / delete aborted (no consent)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
COMPSKILL_DIR = SKILL_DIR.parent
AUDIT_SCRIPT = COMPSKILL_DIR.parent / "planning-version-coverage-audit" / "scripts" / "audit-version-coverage.py"

# Terms that mark a reference as a TRACE (Change-History-style provenance) rather
# than STALE (dead linkage) — the command word indicates a historical record.
TRACE_TERMS = (
    "supersed", "retired", "removed", "trash", "covered", "history",
    "change history", "changelog", "v1", "v2", "original", "initial",
)

REF_RE = re.compile(r"(?:`?[^\\s`]+)?([A-Za-z0-9._+\\-]+_(?:plan|task|commit-preview)_?[A-Za-z0-9._-]*_v\\d+\\.md)")

TRACE_RE = re.compile("|".join(re.escape(t) for t in TRACE_TERMS), re.IGNORECASE)


def error(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def run_audit(old: Path, new: Path) -> dict:
    if not AUDIT_SCRIPT.is_file():
        raise FileNotFoundError(f"coverage gate script not found: {AUDIT_SCRIPT}")
    result = subprocess.run(
        [sys.executable, str(AUDIT_SCRIPT), "--old", str(old), "--new", str(new), "--json"],
        capture_output=True,
        text=True,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"coverage gate returned unusable output: {result.stdout or result.stderr}")


def base_name(path: Path) -> str:
    return path.name


def find_stale_refs(root: Path, old_name: str) -> list[dict]:
    """Walk root for markdown files referencing the old file's exact path/name.

    Returns a list of {file, line, kind, snippet} — kind = TRACE | STALE.
    """
    hits: list[dict] = []
    for path in sorted(root.rglob("*.md")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for idx, line in enumerate(lines, start=1):
            if old_name in line:
                hits.append(
                    {
                        "file": str(path),
                        "line": idx,
                        "snippet": line.strip()[:160],
                        "kind": "TRACE" if TRACE_RE.search(line) else "STALE",
                    }
                )
    return hits


def dump_json(obj: object) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Retire a superseded versioned artifact")
    ap.add_argument("--old", required=True, help="retiring artifact path (v1)")
    ap.add_argument("--new", required=True, help="surviving artifact path (v2)")
    ap.add_argument("--asset-root", default=None, help="root for the stale sweep (default: old file's docs ancestor)")
    ap.add_argument("--dry-run", action="store_true", help="compute + print audit verdict and the stale-ref plan; NO writes")
    ap.add_argument("--confirm", default=None, metavar="TOKEN", help="exact authorization token; canonical value DELETE")
    ap.add_argument("--delete", action="store_true", help="deprecated alias — use --confirm")
    ap.add_argument("--verify", action="store_true", help="scan assert zero STALE refs post-deletion; exit 0/1")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    old_path = Path(args.old)
    new_path = Path(args.new)
    if not old_path.is_file():
        error(f"--old not found: {old_path}")
        return 2
    if not new_path.is_file():
        error(f"--new not found: {new_path}")
        return 2

    root = Path(args.asset_root) if args.asset_root else old_path.parent
    old_name = old_path.name

    # ---- GATE 1: coverage ----------------------------------------------------
    try:
        audit = run_audit(old_path, new_path)
    except (FileNotFoundError, RuntimeError) as exc:
        error(str(exc))
        return 1

    if args.verify:
        rescan = [h for h in find_stale_refs(root, old_name) if h["kind"] == "STALE"]
        if args.json:
            dump_json({"verify": True, "stale_remaining": len(rescan), "stale_hits": rescan})
        else:
            print(f"verify: {len(rescan)} STALE reference(s) to {old_name}")
            for hit in rescan:
                print(f"  {hit['file']}:{hit['line']}  {hit['snippet']}")
        return 0 if not rescan else 1

    if args.dry_run:
        cached = find_stale_refs(root, old_name)
        stale = [h for h in cached if h["kind"] == "STALE"]
        if args.json:
            out = {
                "mode": "dry-run",
                "coverage_verdict": audit.get("verdict"),
                "old": str(old_path),
                "new": str(new_path),
                "stats": dict((k, audit[k]) for k in ("old_sections", "new_sections")),
                "stale_refs": stale,
                "would_trash": [["trash", str(old_path)]],
            }
            print(json.dumps(out, indent=2, sort_keys=True))
        else:
            print(f"coverage verdict: {audit.get('verdict')}")
            print()
            print(f"plans to trash:  {old_name}")
            print(f"stale references found: {len(stale)}")
            for hit in stale:
                print(f"  {hit['file']}:{hit['line']}  {hit['snippet']}")
            if not stale:
                print("(no STALE references outside TRACE rows; task.md may need re-sync manually)")
        return 0 if audit.get("verdict") == "FULL" else 1

    # ---- GATE 2 + MUTATION: user authorization token (authorized DELETION) ---
    if audit.get("verdict") != "FULL":
        print(f"abort: coverage verdict is {audit.get('verdict')} — FULL required")
        return 1

    if args.confirm != "DELETE":
        print('abort: --confirm DELETE not provided (authorization gate) — nothing deleted')
        return 3

    if not shutil.which("trash"):
        print("abort: `trash` binary not found on macOS — `rm` is forbidden; nothing deleted")
        return 1

    stale = [h for h in find_stale_refs(root, old_name) if h["kind"] == "STALE"]
    for hit in stale:
        # Prose-level rewriting of STALE prose/link rows (AGENTS-legacy table
        # rows, "v1 intact" claims, task.md links) is owned by the SKILL.md
        # procedure tier, not by this script — the script only mutates via `trash`.
        if not args.json:
            print(f"STALE after retirement (rebase via SKILL.md procedure): {hit['file']}:{hit['line']}")

    subprocess.run(["trash", str(old_path)], check=True)

    if args.json:
        dump_json({"deleted": str(old_path), "stale_to_rebase": [h["file"] for h in stale]})
    else:
        print(f"retired via trash: {old_name}")
        if stale:
            print(f"STALE references remain in {len(stale)} file(s) — run the prose rebase pass, then --verify")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))