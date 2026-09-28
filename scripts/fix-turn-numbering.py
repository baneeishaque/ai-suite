#!/usr/bin/env python3
"""Fix turn YAML numbering: remove byte-identical duplicates, flag diverged files."""

import json, re, subprocess, sys, hashlib
from pathlib import Path
from datetime import datetime


def trash(path):
    subprocess.run(["trash", str(path)], capture_output=True)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm_ts(s):
    date_part, rest = s.split("T", 1)
    parts = rest.rsplit("-", 3)
    return date_part + "T" + ":".join(parts[:2]) + ":" + parts[2] + "." + parts[3].rstrip("Z")


def load_turns(jsonl_path):
    events = []
    with open(jsonl_path) as f:
        for line in f:
            obj = json.loads(line)
            if obj.get("type") == "turn.complete":
                events.append((obj["turnIndex"], obj["timestamp"]))
    return events


def fix_session(sid, log_dir, dry_run=True):
    turn_dir = log_dir / sid
    if not turn_dir.is_dir():
        print(f"  SKIP: no turn dir for {sid}")
        return
    jsonl = log_dir / f"{sid}.jsonl"
    if not jsonl.exists():
        print(f"  SKIP: no JSONL for {sid}")
        return

    turns = load_turns(jsonl)
    if not turns:
        print(f"  SKIP: no turn.complete events in JSONL")
        return

    turn_dts = [(ti, datetime.fromisoformat(ts.rstrip("Z"))) for ti, ts in turns]

    # Parse all YAML files
    yaml_files = []
    for y in sorted(turn_dir.glob("*.yaml")):
        if y.name.startswith("000-header"):
            continue
        m = re.match(r"(\d+)-(.+)\.yaml", y.name)
        if not m:
            continue
        y_num = int(m.group(1))
        y_dt = datetime.fromisoformat(norm_ts(m.group(2)).rstrip("Z"))
        best_idx = min(
            range(len(turn_dts)),
            key=lambda i: abs((y_dt - turn_dts[i][1]).total_seconds()),
        )
        diff = abs((y_dt - turn_dts[best_idx][1]).total_seconds())
        ti = turn_dts[best_idx][0]
        yaml_files.append((y_num, diff, y, ti))

    # Pass 1: identify canonical files (within 2s of a turn.complete)
    canonicals: dict[int, Path] = {}  # turnIndex -> Path
    for y_num, diff, y, ti in yaml_files:
        if diff < 2.0 and ti not in canonicals:
            canonicals[ti] = y

    # Build sha map for canonical files keyed by their CURRENT turn number
    canonical_sha = {}  # turn_number -> sha
    for ti, y in canonicals.items():
        expected = ti + 1
        m = re.match(r"(\d+)-", y.name)
        current_num = int(m.group(1))
        canonical_sha[current_num] = sha256(y)

    # Pass 2: classify every file
    kept = 0
    deleted = 0
    diverged = 0
    rename_ops = []

    for y_num, diff, y, ti in yaml_files:
        is_canonical = y in canonicals.values()
        if is_canonical:
            kept += 1
            expected_num = ti + 1
            if y_num != expected_num:
                new_name = f"{expected_num:03d}-{y.name.split('-', 1)[1]}"
                new_path = turn_dir / new_name
                if new_path.exists():
                    print(f"    ERROR: {new_name} exists, cannot rename {y.name}")
                else:
                    rename_ops.append((y, new_path))
            continue

        # Non-canonical: check if ditto to a canonical with the SAME turn number
        if y_num in canonical_sha and sha256(y) == canonical_sha[y_num]:
            print(f"    DELETE {y.name} (ditto canonical for turn {y_num:03d})")
            if not dry_run:
                trash(str(y))
            deleted += 1
        else:
            print(f"    DIVERGED {y.name} (no matching canonical) — KEEPING")
            diverged += 1

    for old_path, new_path in rename_ops:
        if not dry_run:
            old_path.rename(new_path)
        print(f"    RENAME {old_path.name} → {new_path.name}")

    print(f"  {sid}: {kept} kept, {deleted} deleted, {diverged} diverged, {len(rename_ops)} renamed")


if __name__ == "__main__":
    log_dir = Path(__file__).resolve().parent.parent / ".opencode" / "logs"
    dry_run = "--dry-run" in sys.argv
    sids = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not sids:
        print("Usage: fix-turn-numbering.py [--dry-run] <ses_id_1> [ses_id_2 ...]")
        sys.exit(1)
    for sid in sids:
        print(f"--- {sid} ---")
        fix_session(sid, log_dir, dry_run=dry_run)
