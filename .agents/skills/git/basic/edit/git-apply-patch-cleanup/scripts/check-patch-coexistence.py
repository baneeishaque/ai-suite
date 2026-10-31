#!/usr/bin/env python3
"""check-patch-coexistence.py — Preflight whether candidate patch B coexists with pre-state patch A.

Rebuilds ``base-ref`` in an isolated worktree, applies patch A, then tries
patch B plain; if that fails, it commits A and retries B with ``git apply
--3way``. Every file touched by B is classified across four dimensions:

* ``line`` — plain-apply result (``clean``, ``conflict``, ``failed``).
* ``content`` — conflict markers present after the three-way retry.
* ``knowledge`` — both patches touch the same document category.
* ``structure`` — both patches touch the same file.

Usage:
    python3 check-patch-coexistence.py --repo <repo> --base-ref <sha> \\
        --pre-state-patch <a.patch> --candidate-patch <b.patch> [--json]

Exit codes: 0 = B coexists, 1 = B does not coexist, 2 = error.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CONFLICT_START = "<<<<<<<"
CONFLICT_MID = "======="
CONFLICT_END = ">>>>>>>"


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and optionally raise on failure."""
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(f"{' '.join(cmd)} failed ({proc.returncode}): {detail}")
    return proc


def patch_paths(patch: Path, cwd: Path) -> set[str]:
    """Return the paths a patch touches via ``git apply --numstat``."""
    proc = run(
        ["git", "-c", "core.quotePath=false", "apply", "--numstat", str(patch)],
        cwd,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(f"cannot read patch {patch}: {detail}")
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            paths.add(parts[2])
    return paths


def has_conflict_markers(path: Path) -> bool:
    """Return True when the file carries a full conflict-marker block."""
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return (
        CONFLICT_START in text
        and CONFLICT_MID in text
        and CONFLICT_END in text
    )


def category(rel: str) -> str:
    """Classify a path into a documentation/code category."""
    name = Path(rel).name
    if name == "CHANGELOG.md":
        return "changelog"
    if name == "TRACEABILITY.md":
        return "traceability"
    if name in {"SKILL.md", "AGENTS.md"}:
        return "skill_doc"
    return "code"


def classify(
    worktree: Path,
    pre_paths: set[str],
    candidate_paths: set[str],
    plain_ok: bool,
    three_way_ok: bool,
    three_way_ran: bool,
) -> list[dict]:
    """Classify every candidate-touched file across the four dimensions."""
    changed = set()
    proc = run(["git", "diff", "--name-only", "HEAD"], worktree, check=False)
    if proc.returncode == 0:
        changed = {line for line in proc.stdout.splitlines() if line}
    records: list[dict] = []
    for rel in sorted(candidate_paths):
        target = worktree / rel
        markers = has_conflict_markers(target)
        if markers:
            line_status = "conflict"
        elif plain_ok:
            line_status = "clean"
        elif rel in changed:
            line_status = "clean"
        else:
            line_status = "failed"
        same_file = rel in pre_paths
        same_category = any(category(rel) == category(pre) for pre in pre_paths)
        records.append(
            {
                "path": rel,
                "touched_by_pre_state": same_file,
                "line": line_status,
                "content": "conflict_markers" if markers else "clean",
                "knowledge": "same_category" if same_category else "disjoint",
                "structure": "same_file" if same_file else "disjoint",
                "category": category(rel),
            }
        )
    return records


def emit_text(report: dict) -> None:
    """Print a human-readable report."""
    print(f"pre-state applied: {report['pre_state_applied']}")
    print(f"candidate plain:   {report['plain']['status']}")
    print(f"candidate 3-way:   {report['three_way']['status']}")
    for record in report["files"]:
        print(
            f"{record['path']}: line={record['line']} "
            f"content={record['content']} knowledge={record['knowledge']} "
            f"structure={record['structure']}"
        )
    print(f"coexists: {report['coexists']}")
    if report["conflict_files"]:
        print("conflict files: " + ", ".join(report["conflict_files"]))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preflight whether candidate patch B coexists with pre-state patch A."
    )
    parser.add_argument("--repo", default=".", help="Repository root (default: cwd)")
    parser.add_argument("--base-ref", required=True, help="Commit both patches are layered on")
    parser.add_argument("--pre-state-patch", required=True, help="Patch A, applied first")
    parser.add_argument("--candidate-patch", required=True, help="Patch B, applied on top of A")
    parser.add_argument(
        "--workdir",
        help="Parent directory for the isolated worktree (default: <repo>/scratch)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument(
        "--keep-worktree", action="store_true", help="Keep the isolated worktree"
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    pre_patch = Path(args.pre_state_patch).resolve()
    candidate_patch = Path(args.candidate_patch).resolve()
    for label, patch in (("pre-state", pre_patch), ("candidate", candidate_patch)):
        if not patch.is_file():
            print(f"ERROR: {label} patch not found: {patch}", file=sys.stderr)
            sys.exit(2)

    workdir_parent = (
        Path(args.workdir).resolve() if args.workdir else repo / "scratch"
    )
    workdir_parent.mkdir(parents=True, exist_ok=True)
    base = Path(tempfile.mkdtemp(prefix="patch-coexistence-", dir=workdir_parent))
    worktree = base / "wt"

    try:
        run(
            [
                "git",
                "-c",
                "core.hooksPath=/dev/null",
                "worktree",
                "add",
                "--detach",
                "--quiet",
                str(worktree),
                args.base_ref,
            ],
            repo,
        )
        pre_paths = patch_paths(pre_patch, worktree)
        candidate_paths = patch_paths(candidate_patch, worktree)

        run(["git", "apply", str(pre_patch)], worktree)
        pre_state_applied = True
        if run(["git", "diff", "--quiet"], worktree, check=False).returncode != 0:
            run(["git", "add", "-A"], worktree)
            run(
                [
                    "git",
                    "-c",
                    "user.name=patch-coexistence",
                    "-c",
                    "user.email=patch-coexistence@localhost",
                    "commit",
                    "-q",
                    "-m",
                    "pre-state",
                ],
                worktree,
            )

        plain = run(["git", "apply", str(candidate_patch)], worktree, check=False)
        plain_ok = plain.returncode == 0
        plain_record = {
            "status": "ok" if plain_ok else "failed",
            "exit": plain.returncode,
            "stderr": plain.stderr.strip(),
        }

        three_way_ran = False
        three_way_ok = False
        three_way_record = {
            "status": "skipped",
            "exit": None,
            "stderr": "",
        }
        if not plain_ok:
            run(["git", "reset", "--hard", "HEAD"], worktree)
            three_way_ran = True
            three_way = run(
                ["git", "apply", "--3way", str(candidate_patch)],
                worktree,
                check=False,
            )
            three_way_ok = three_way.returncode == 0
            three_way_record = {
                "status": "ok" if three_way_ok else "conflict",
                "exit": three_way.returncode,
                "stderr": three_way.stderr.strip(),
            }

        records = classify(
            worktree,
            pre_paths,
            candidate_paths,
            plain_ok,
            three_way_ok,
            three_way_ran,
        )
    except (RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    finally:
        if not args.keep_worktree:
            run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                repo,
                check=False,
            )
            shutil.rmtree(base, ignore_errors=True)
            run(["git", "worktree", "prune"], repo, check=False)

    conflict_files = [
        record["path"]
        for record in records
        if record["line"] == "conflict" or record["content"] == "conflict_markers"
    ]
    coexists = plain_ok or (
        three_way_ran and three_way_ok and not conflict_files
    )
    report = {
        "repo": str(repo),
        "base_ref": args.base_ref,
        "pre_state_patch": str(pre_patch),
        "candidate_patch": str(candidate_patch),
        "pre_state_applied": pre_state_applied,
        "plain": plain_record,
        "three_way": three_way_record,
        "files": records,
        "conflict_files": conflict_files,
        "coexists": coexists,
        "dimensions": {
            "line": {
                "clean": sum(1 for record in records if record["line"] == "clean"),
                "conflict": sum(1 for record in records if record["line"] == "conflict"),
                "failed": sum(1 for record in records if record["line"] == "failed"),
            },
            "content": {
                "conflict_markers": sum(
                    1 for record in records if record["content"] == "conflict_markers"
                )
            },
            "knowledge": {
                "same_category": sum(
                    1 for record in records if record["knowledge"] == "same_category"
                )
            },
            "structure": {
                "same_file": sum(
                    1 for record in records if record["structure"] == "same_file"
                )
            },
        },
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        emit_text(report)
    if args.keep_worktree:
        print(f"Worktree kept at: {worktree}", file=sys.stderr)
    sys.exit(0 if coexists else 1)


if __name__ == "__main__":
    main()
