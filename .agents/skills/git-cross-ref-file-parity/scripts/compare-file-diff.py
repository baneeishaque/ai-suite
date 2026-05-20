#!/usr/bin/env python3
"""
compare-file-diff.py — Compare the diff introduced for a specific file by a
commit versus a stash (or any two git refs) and report IDENTICAL or DIFFERENT.

Usage
-----
    # Commit SHA vs stash by name:
    python3 compare-file-diff.py \
        --repo /path/to/repo \
        --commit <SHA> \
        --stash  before-nginx-on-agents-md \
        --file   AGENTS.md

    # Commit SHA vs stash by ref:
    python3 compare-file-diff.py \
        --repo /path/to/repo \
        --commit <SHA> \
        --stash  "stash@{0}" \
        --file   AGENTS.md

    # Any two arbitrary refs (both treated as commits):
    python3 compare-file-diff.py \
        --repo /path/to/repo \
        --ref-a <SHA-or-branch-A> \
        --ref-b <SHA-or-branch-B> \
        --file  AGENTS.md

    # Always print both diffs (even when identical):
    python3 compare-file-diff.py ... --show-diff

Ref resolution
--------------
- --commit  : compared against its parent (<commit>^ vs <commit>)
- --stash   : compared against its base  (stash^1 vs stash^0)
              If given as a human name (e.g. "before-nginx-on-agents-md"),
              resolved by scanning `git stash list`.
- --ref-a / --ref-b : generic refs; each compared against its own parent.

Output
------
    IDENTICAL  — both diffs (stripped of path headers) are byte-for-byte equal
    DIFFERENT  — diffs diverge; unified diff-of-diffs is printed

Exit codes
----------
    0  IDENTICAL
    1  DIFFERENT
    2  Error (bad args, git failure, unresolved stash name)
"""

from __future__ import annotations
import argparse, re, subprocess, sys
from pathlib import Path


def run(cmd: list, repo: str) -> str:
    r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ERROR: {' '.join(cmd)}\n{r.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    return r.stdout


def resolve_stash(name_or_ref: str, repo: str) -> str:
    if re.match(r'^stash@\{\d+\}$', name_or_ref):
        return name_or_ref
    listing = subprocess.run(
        ["git", "--no-pager", "stash", "list"],
        cwd=repo, capture_output=True, text=True
    ).stdout
    for line in listing.splitlines():
        if name_or_ref in line:
            return line.split(":")[0].strip()
    print(f"ERROR: stash name '{name_or_ref}' not found.", file=sys.stderr)
    print(f"Available stashes:\n{listing or '  (none)'}", file=sys.stderr)
    sys.exit(2)


def get_diff(repo: str, base: str, tip: str, filepath: str) -> str:
    return run(["git", "--no-pager", "diff", base, tip, "--", filepath], repo)


def normalise(diff: str) -> str:
    """Strip path-specific headers (diff --git, index, ---, +++) before comparing."""
    lines = [
        l for l in diff.splitlines()
        if not re.match(r'^(diff --git|index [0-9a-f]+|--- a/|\+\+\+ b/)', l)
    ]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(
        description="Compare a file's diff between a commit and a stash (or any two refs).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--repo", default=".", metavar="DIR",
                   help="Repository root (default: current directory).")
    p.add_argument("--file", required=True, metavar="PATH",
                   help="File path relative to repo root.")
    p.add_argument("--commit", metavar="SHA",
                   help="Commit ref — compared against its parent.")
    p.add_argument("--stash", metavar="REF-OR-NAME",
                   help="Stash ref or human name — compared against its base (stash^1 vs stash^0).")
    p.add_argument("--ref-a", metavar="REF",
                   help="First generic ref — compared against its parent.")
    p.add_argument("--ref-b", metavar="REF",
                   help="Second generic ref — compared against its parent.")
    p.add_argument("--show-diff", action="store_true",
                   help="Always print both raw diffs, even when IDENTICAL.")
    args = p.parse_args()

    repo = str(Path(args.repo).resolve())

    if args.commit and args.stash:
        label_a = f"commit {args.commit[:12]}"
        diff_a  = get_diff(repo, f"{args.commit}^", args.commit, args.file)
        stash_ref = resolve_stash(args.stash, repo)
        label_b = f"stash  {stash_ref} ({args.stash})"
        diff_b  = get_diff(repo, f"{stash_ref}^1", f"{stash_ref}^0", args.file)
    elif args.ref_a and args.ref_b:
        label_a = f"ref-a  {args.ref_a}"
        diff_a  = get_diff(repo, f"{args.ref_a}^", args.ref_a, args.file)
        label_b = f"ref-b  {args.ref_b}"
        diff_b  = get_diff(repo, f"{args.ref_b}^", args.ref_b, args.file)
    else:
        p.error("Provide either (--commit + --stash) or (--ref-a + --ref-b).")

    norm_a, norm_b = normalise(diff_a), normalise(diff_b)

    print(f"File   : {args.file}")
    print(f"Side A : {label_a}  ({len(diff_a.splitlines())} diff lines)")
    print(f"Side B : {label_b}  ({len(diff_b.splitlines())} diff lines)")
    print()

    if args.show_diff or norm_a != norm_b:
        print("=== Side A diff ===")
        print(diff_a or "  (empty — file not changed by this ref)")
        print("=== Side B diff ===")
        print(diff_b or "  (empty — file not changed by this ref)")

    if norm_a == norm_b:
        print("Result : ✅  IDENTICAL — changes are byte-for-byte equal (after header normalisation)")
        sys.exit(0)
    else:
        print("Result : ❌  DIFFERENT — diffs diverge")
        import difflib
        delta = list(difflib.unified_diff(
            norm_a.splitlines(), norm_b.splitlines(),
            fromfile="side-A", tofile="side-B", lineterm=""
        ))
        if delta:
            print("\n=== Diff-of-diffs (A → B) ===")
            print("\n".join(delta))
        sys.exit(1)


if __name__ == "__main__":
    main()
