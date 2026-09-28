#!/usr/bin/env python3
"""Backup opencode sessions: copy active sessions, move dead sessions from logs to exports."""

import hashlib
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


def file_match(src: Path, dst: Path) -> bool | None:
    """Return True if files match, False if mismatch, None if dst missing."""
    if not dst.exists():
        return None
    try:
        return (
            hashlib.file_digest(src.open("rb"), "sha256").hexdigest()
            == hashlib.file_digest(dst.open("rb"), "sha256").hexdigest()
        )
    except Exception:
        return False


def jsonl_is_updated(src: Path, dst: Path) -> bool:
    """Check if src .jsonl is a superset of dst (export is a prefix of log)."""
    try:
        src_lines = src.read_text(errors="replace").splitlines(keepends=True)
        dst_lines = dst.read_text(errors="replace").splitlines(keepends=True)
        if len(src_lines) < len(dst_lines):
            return False
        return src_lines[:len(dst_lines)] == dst_lines
    except Exception:
        return False


def trash(path):
    subprocess.run(["trash", str(path)], capture_output=True)

WORK_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = WORK_DIR / ".opencode" / "logs"
EXPORT_DIR = WORK_DIR / "ai-session-exports" / "opencode-session-exports"
DB_PATH = Path.home() / ".local" / "share" / "opencode" / "opencode.db"

DRY_RUN = "--dry-run" in sys.argv


def log(msg=""):
    print(msg)


def fmt_size(n: int) -> str:
    if n > 1_000_000:
        return f"{n/1_000_000:.1f}MB"
    if n > 1_000:
        return f"{n/1_000:.0f}KB"
    return f"{n}B"


def active_session_ids() -> set[str]:
    if not DB_PATH.exists():
        log(f"WARNING: DB not found at {DB_PATH}")
        return set()
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("SELECT id FROM session")
    ids = {row[0] for row in cur.fetchall()}
    conn.close()
    log(f"DB: {len(ids)} active sessions")
    return ids


def scan_logs():
    files: dict[str, list[Path]] = {}
    dirs: dict[str, Path] = {}
    for entry in LOG_DIR.iterdir():
        name = entry.name
        if entry.is_file():
            if not name.startswith("ses_"):
                continue
            sid = name.split(".", 1)[0]
            if sid.endswith(".turns"):
                sid = sid[:-6]
            files.setdefault(sid, []).append(entry)
        elif entry.is_dir() and name.startswith("ses_"):
            dirs[name] = entry
    for sid in list(dirs.keys()):
        if sid not in files:
            files[sid] = []
    return files, dirs


def find_sub_agents(files: dict[str, list[Path]]) -> dict[str, set[str]]:
    import json as _json
    parent_map: dict[str, str] = {}
    for sid, paths in files.items():
        jsonl = None
        for p in paths:
            if p.suffix == ".jsonl" and not p.name.endswith(".turns.jsonl"):
                jsonl = p
                break
        if not jsonl:
            continue
        try:
            text = jsonl.read_text(errors="replace")
        except Exception:
            continue
        try:
            for line in text.splitlines():
                if '"session.sub_created"' not in line:
                    continue
                try:
                    obj = _json.loads(line)
                except Exception:
                    continue
                if obj.get("type") == "session.sub_created":
                    child = obj.get("sessionID")
                    if child and child != sid:
                        parent_map[child] = sid
        except Exception:
            continue
    children: dict[str, set[str]] = {}
    for child, parent in parent_map.items():
        children.setdefault(parent, set()).add(child)
    return children


def backup():
    active = active_session_ids()
    session_files, session_dirs = scan_logs()
    sub_agents = find_sub_agents(session_files)

    skipped_children: set[str] = set()
    for children in sub_agents.values():
        skipped_children.update(children)

    log(f"Scanned: {len(session_files)} sessions ({len(sub_agents)} parents, {len(skipped_children)} sub-agents)\n")

    log("Tree view:")
    for sid in sorted(session_files):
        if sid in skipped_children:
            continue
        is_active = sid in active
        action = "COPY" if is_active else "MOVE"
        children = sub_agents.get(sid, set())
        files = session_files[sid]
        turn_dir = session_dirs.get(sid)
        label = sid
        parts = [f"  [{action}] {label}"]
        parts.append(f"({len(files)} files)")
        if turn_dir:
            parts.append("[+dir]")
        if children:
            parts.append(f"← {len(children)} sub")
        log(" ".join(parts))
        for child in sorted(children):
            cf = session_files.get(child, [])
            cd = session_dirs.get(child)
            cl = child
            cp = [f"  │  └─ {cl}"]
            cp.append(f"({len(cf)} files)")
            if cd:
                cp.append("[+dir]")
            log(" ".join(cp))
    log("")

    counts = {"copied": 0, "moved": 0, "errors": 0}
    total_bytes = 0

    for sid in sorted(session_files.keys()):
        if sid in skipped_children:
            continue

        is_active = sid in active
        action = "COPY" if is_active else "MOVE"
        children = sub_agents.get(sid, set())

        files = session_files[sid]
        turn_dir = session_dirs.get(sid)
        dest = EXPORT_DIR / sid

        try:
            if not DRY_RUN:
                dest.mkdir(parents=True, exist_ok=True)
            file_ops = []

            for src in sorted(files):
                dst = dest / src.name
                match = file_match(src, dst)
                if match is True:
                    file_ops.append(f"{src.name} ✓ matched")
                    if not is_active and not DRY_RUN:
                        trash(str(src))
                    continue
                elif match is False:
                    if src.suffix == ".jsonl" and jsonl_is_updated(src, dst):
                        file_ops.append(f"{src.name} ✓ updated (log is superset of export)")
                    else:
                        file_ops.append(f"{src.name} ✗ MISMATCH (log vs export differ)")
                        counts["errors"] += 1
                    continue
                total_bytes += src.stat().st_size
                if not DRY_RUN:
                    if is_active:
                        shutil.copy2(src, dst)
                    else:
                        shutil.move(str(src), str(dst))
                file_ops.append(f"{src.name} → new to export")

            if turn_dir:
                dst_turn = dest / turn_dir.name
                if dst_turn.exists():
                    for f in sorted(turn_dir.iterdir()):
                        d = dst_turn / f.name
                        dm = file_match(f, d)
                        if dm is True:
                            file_ops.append(f"{turn_dir.name}/{f.name} ✓ matched")
                        elif dm is False:
                            msg = f"{turn_dir.name}/{f.name} ✗ MISMATCH"
                            file_ops.append(msg)
                            counts["errors"] += 1
                        else:
                            total_bytes += f.stat().st_size
                            if not DRY_RUN:
                                if is_active:
                                    shutil.copy2(f, d)
                                else:
                                    shutil.move(str(f), str(d))
                            file_ops.append(f"{turn_dir.name}/{f.name} → new to export")
                    if not is_active and not DRY_RUN:
                        remaining = list(turn_dir.iterdir())
                        if not remaining:
                            try:
                                turn_dir.rmdir()
                            except OSError:
                                pass
                else:
                    sz = sum(f.stat().st_size for f in turn_dir.rglob("*") if f.is_file())
                    total_bytes += sz
                    if not DRY_RUN:
                        if is_active:
                            shutil.copytree(str(turn_dir), str(dst_turn))
                        else:
                            shutil.move(str(turn_dir), str(dst_turn))
                    file_ops.append(f"{turn_dir.name}/ → new to export")

            for child in sorted(children):
                child_dest = dest / child
                if not DRY_RUN:
                    child_dest.mkdir(parents=True, exist_ok=True)
                child_files = session_files.get(child, [])
                child_turn = session_dirs.get(child)
                for src in child_files:
                    cd = child_dest / src.name
                    cm = file_match(src, cd)
                    if cm is True:
                        file_ops.append(f"  sub: {child}/{src.name} ✓ matched")
                        if not is_active and not DRY_RUN:
                            trash(str(src))
                        continue
                    elif cm is False:
                        if src.suffix == ".jsonl" and jsonl_is_updated(src, cd):
                            file_ops.append(f"  sub: {child}/{src.name} ✓ updated (log is superset of export)")
                        else:
                            file_ops.append(f"  sub: {child}/{src.name} ✗ MISMATCH")
                            counts["errors"] += 1
                        continue
                    total_bytes += src.stat().st_size
                    if not DRY_RUN:
                        if is_active:
                            shutil.copy2(src, cd)
                        else:
                            shutil.move(str(src), str(cd))
                if child_turn:
                    cd_turn = child_dest / child_turn.name
                    if cd_turn.exists():
                        for f in sorted(child_turn.iterdir()):
                            d = cd_turn / f.name
                            cm = file_match(f, d)
                            if cm is True:
                                file_ops.append(f"  sub: {child}/{child_turn.name}/{f.name} ✓ matched")
                            elif cm is False:
                                msg = f"  sub: {child}/{child_turn.name}/{f.name} ✗ MISMATCH"
                                file_ops.append(msg)
                                counts["errors"] += 1
                            else:
                                total_bytes += f.stat().st_size
                                if not DRY_RUN:
                                    if is_active:
                                        shutil.copy2(f, d)
                                    else:
                                        shutil.move(str(f), str(d))
                                file_ops.append(f"  sub: {child}/{child_turn.name}/{f.name} → new to export")
                        if not is_active and not DRY_RUN:
                            remaining = list(child_turn.iterdir())
                            if not remaining:
                                try:
                                    child_turn.rmdir()
                                except OSError:
                                    pass
                    else:
                        sz = sum(f.stat().st_size for f in child_turn.rglob("*") if f.is_file())
                        total_bytes += sz
                        if not DRY_RUN:
                            if is_active:
                                shutil.copytree(str(child_turn), str(cd_turn))
                            else:
                                shutil.move(str(child_turn), str(cd_turn))
                        file_ops.append(f"  sub: {child}/{child_turn.name}/ → new to export")

            turn_info = f" +dir {turn_dir.name}" if turn_dir else ""
            child_info = f" +{len(children)} sub" if children else ""
            log(f"  [{action}] {sid}  ({len(files)} files{turn_info}{child_info})")
            for op in file_ops:
                log(f"    {op}")

            counts["copied" if is_active else "moved"] += 1

        except Exception as e:
            log(f"    ERROR [{sid}]: {e}")
            counts["errors"] += 1

    log(f"\n{'='*60}")
    log(f"  Copied (active):         {counts['copied']}")
    log(f"  Moved (dead):            {counts['moved']}")
    log(f"  Errors:                  {counts['errors']}")
    if not DRY_RUN:
        log(f"  Total data transferred:  {fmt_size(total_bytes)}")
    log(f"{'='*60}")


if __name__ == "__main__":
    backup()
