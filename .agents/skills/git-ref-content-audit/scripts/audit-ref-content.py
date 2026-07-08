#!/usr/bin/env python3
"""
audit-ref-content.py — Bulk per-file blob-equality audit between two Git refs.

Enumerates every file present in REF-A (including the untracked tree branch of
a stash via `<stash>^3`) and classifies each path against REF-B:

    IDENTICAL  — blob hash at REF-A equals blob hash at REF-B
    DIFFERENT  — both refs have the path but blobs differ
    MISSING    — REF-A has the path but REF-B does not

Reports counts, per-file status, and (optionally) a unified diff for DIFFERENT
files. Exits 0 if every REF-A path is present in REF-B (IDENTICAL or
DIFFERENT); exits 1 if any path is MISSING; exits 2 on usage / git errors.

Canonical use case: verify that a safety stash is fully superseded by the
current HEAD before dropping it.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import Optional


# --- git helpers --------------------------------------------------------------

def git(args: list[str], repo: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True, text=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed (exit {result.returncode}): "
            f"{result.stderr.strip()}"
        )
    return result.stdout


def rev_parse(ref: str, repo: str) -> Optional[str]:
    out = git(["rev-parse", "--verify", "--quiet", ref], repo, check=False).strip()
    return out or None


def resolve_stash(name: str, repo: str) -> str:
    """Resolve a stash by name (--stash before-nginx-on-agents-md) or numeric
    index (--stash 0) or pass-through (stash@{N})."""
    if name.startswith("stash@{"):
        if rev_parse(name, repo):
            return name
        raise RuntimeError(f"stash ref not found: {name}")
    if name.isdigit():
        candidate = f"stash@{{{name}}}"
        if rev_parse(candidate, repo):
            return candidate
        raise RuntimeError(f"no stash at index {name}")
    # Resolve by message substring
    listing = git(["stash", "list"], repo).splitlines()
    matches = [line for line in listing if name in line]
    if not matches:
        raise RuntimeError(f"no stash matching: {name!r}")
    if len(matches) > 1:
        raise RuntimeError(
            f"ambiguous stash name {name!r}; matches: " +
            "; ".join(m.split(":", 1)[0] for m in matches)
        )
    return matches[0].split(":", 1)[0]  # "stash@{N}"


def is_stash(ref: str, repo: str) -> bool:
    """A stash commit has 2+ parents; the third parent (^3) is the untracked
    tree when -u was used during `git stash push -u`."""
    if not ref.startswith("stash@{"):
        return False
    return rev_parse(f"{ref}^3", repo) is not None or \
           rev_parse(f"{ref}^2", repo) is not None


def file_blob(ref: str, path: str, repo: str) -> Optional[str]:
    """40-char blob hash of <ref>:<path>, or None if path missing under ref."""
    result = subprocess.run(
        ["git", "-C", repo, "rev-parse", "--verify", "--quiet", f"{ref}:{path}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    h = result.stdout.strip()
    return h if len(h) == 40 else None


# --- enumeration --------------------------------------------------------------

def files_in_ref(ref: str, repo: str, include_untracked: bool) -> dict[str, str]:
    """Return {path: blob_hash} for every file accessible under REF.

    For commits: enumerate the full tree via `ls-tree -r`.
    For stashes: union of tracked-diff (vs ref^1) and untracked tree (ref^3).
    """
    files: dict[str, str] = {}

    if ref.startswith("stash@{"):
        # Tracked changes: files in the stash commit's tree that differ from its
        # first parent (the WORKING tree at stash time).
        out = git(
            ["diff-tree", "-r", "--name-only", "--no-commit-id", ref, f"{ref}^1"],
            repo,
        )
        for path in (l for l in out.splitlines() if l.strip()):
            h = file_blob(ref, path, repo)
            if h:
                files[path] = h

        # Untracked tree (only present if stash was created with -u)
        if include_untracked:
            utree = rev_parse(f"{ref}^3", repo)
            if utree:
                out = git(["ls-tree", "-r", utree], repo)
                for line in out.splitlines():
                    parts = line.split(None, 3)
                    if len(parts) < 4:
                        continue
                    _mode, _typ, blob, path = parts
                    files.setdefault(path, blob)
        return files

    # Regular ref (commit / branch / tag): walk the tree
    out = git(["ls-tree", "-r", ref], repo)
    for line in out.splitlines():
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        _mode, typ, blob, path = parts
        if typ == "blob":
            files[path] = blob
    return files


# --- classification -----------------------------------------------------------

@dataclass
class FileVerdict:
    path: str
    status: str           # IDENTICAL | DIFFERENT | MISSING
    ref_a_blob: str
    ref_b_blob: Optional[str]


def classify(ref_a_files: dict[str, str], ref_b: str, repo: str) -> list[FileVerdict]:
    verdicts: list[FileVerdict] = []
    for path, a_blob in sorted(ref_a_files.items()):
        b_blob = file_blob(ref_b, path, repo)
        if b_blob is None:
            verdicts.append(FileVerdict(path, "MISSING", a_blob, None))
        elif a_blob == b_blob:
            verdicts.append(FileVerdict(path, "IDENTICAL", a_blob, b_blob))
        else:
            verdicts.append(FileVerdict(path, "DIFFERENT", a_blob, b_blob))
    return verdicts


# --- reporting ----------------------------------------------------------------

ICONS = {"IDENTICAL": "✅", "DIFFERENT": "🔄", "MISSING": "❌"}


def report_text(verdicts: list[FileVerdict], ref_a: str, ref_b: str,
                show_diffs: bool, repo: str) -> None:
    by_status = {s: [v for v in verdicts if v.status == s]
                 for s in ("IDENTICAL", "DIFFERENT", "MISSING")}

    print(f"Ref A: {ref_a}")
    print(f"Ref B: {ref_b}")
    print(f"Files audited: {len(verdicts)}\n")

    for status in ("IDENTICAL", "DIFFERENT", "MISSING"):
        bucket = by_status[status]
        if not bucket:
            continue
        print(f"=== {ICONS[status]} {status} ({len(bucket)}) ===")
        for v in bucket:
            print(f"  {v.path}")
        print()

    if show_diffs and by_status["DIFFERENT"]:
        print("=== Per-file diffs (DIFFERENT) ===")
        for v in by_status["DIFFERENT"]:
            print(f"\n--- {v.path} ---")
            try:
                diff = git(
                    ["diff", "--no-color",
                     f"{ref_a}:{v.path}", f"{ref_b}:{v.path}"],
                    repo, check=False,
                )
                print(diff if diff.strip() else "(empty diff)")
            except RuntimeError as exc:
                print(f"(diff failed: {exc})")

    # Verdict line
    n_missing = len(by_status["MISSING"])
    n_diff = len(by_status["DIFFERENT"])
    if n_missing == 0 and n_diff == 0:
        verdict = "✅ FULLY SUPERSEDED — every Ref-A file is byte-identical in Ref-B."
    elif n_missing == 0:
        verdict = (f"⚠️ PARTIALLY SUPERSEDED — every Ref-A path exists in Ref-B, "
                   f"but {n_diff} file(s) differ (likely refined later).")
    else:
        verdict = (f"❌ NOT SUPERSEDED — {n_missing} Ref-A file(s) absent from "
                   f"Ref-B; manual disposition required.")
    print(f"\nVERDICT: {verdict}")


# --- main ---------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(
        description="Bulk per-file blob-equality audit between two Git refs.",
    )
    p.add_argument("--repo", required=True, help="Path to the Git repository.")
    ref_a = p.add_mutually_exclusive_group(required=True)
    ref_a.add_argument("--ref-a", help="Ref A (commit SHA / branch / tag).")
    ref_a.add_argument("--stash",
                       help="Stash specifier: stash@{N}, numeric index, or "
                            "message substring.")
    p.add_argument("--ref-b", default="HEAD",
                   help="Ref B (default: HEAD).")
    p.add_argument("--no-untracked", action="store_true",
                   help="For stash Ref A, skip the untracked tree (stash^3).")
    p.add_argument("--show-diffs", action="store_true",
                   help="Print a unified diff for each DIFFERENT file.")
    p.add_argument("--json", action="store_true",
                   help="Emit JSON instead of human-readable text.")
    args = p.parse_args()

    repo = args.repo

    try:
        ref_a_resolved = (resolve_stash(args.stash, repo)
                          if args.stash else args.ref_a)
        if not rev_parse(ref_a_resolved, repo):
            raise RuntimeError(f"Ref A not found: {ref_a_resolved}")
        if not rev_parse(args.ref_b, repo):
            raise RuntimeError(f"Ref B not found: {args.ref_b}")

        files_a = files_in_ref(ref_a_resolved, repo,
                               include_untracked=not args.no_untracked)
        if not files_a:
            print(f"No files enumerable under Ref A: {ref_a_resolved}",
                  file=sys.stderr)
            return 2

        verdicts = classify(files_a, args.ref_b, repo)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({
            "ref_a": ref_a_resolved,
            "ref_b": args.ref_b,
            "files": [asdict(v) for v in verdicts],
        }, indent=2))
    else:
        report_text(verdicts, ref_a_resolved, args.ref_b,
                    args.show_diffs, repo)

    n_missing = sum(1 for v in verdicts if v.status == "MISSING")
    return 1 if n_missing else 0


if __name__ == "__main__":
    sys.exit(main())
