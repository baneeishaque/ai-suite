#!/usr/bin/env python3
"""post-rename-sweep.py — owned by skill-factory §5.1.

Sweep the ai-suite tree for every literal occurrence of an OLD-form string
and (optionally) replace it with a NEW-form, then verify zero residuals.

Use this script for EVERY rename described in skill-factory/SKILL.md §5.1:
  - Heading anchor / section number renumbers (`§3c` -> `§3b`, `§2.3` -> `§2.4`)
  - Skill folder / skill-identifier renames
  - File path / symbol / canonical-placeholder renames
  - Insertion-induced renumbering (new `## N.` bumps successors)

CONTRACT (Tier-A, deterministic):
  Input:  --old <STRING>  --new <STRING>  [--scope <GLOB> ...]  [--apply]
  Output: per-file hit listing (stdout); exit code 0 on no-hits-or-success,
          1 on hits-found-in-dry-run (so a verify pass after --apply exits 0).

USAGE:
  # Dry-run (preview)
  scripts/post-rename-sweep.py --old "§2.3" --new "§2.4"

  # Apply
  scripts/post-rename-sweep.py --old "§2.3" --new "§2.4" --apply

  # Verify zero residual hits
  scripts/post-rename-sweep.py --old "§2.3" --new "§2.4"   # expect exit 0

DEFAULT SCOPES (when --scope not given):
  .agents/skills/**/*.md
  .agents/skills/**/scripts/**/*.py
  .agents/skills/**/scripts/**/*.sh
  .agents/skills/**/scripts/**/*.ps1
  ai-agent-rules/**/*.md
  AGENTS.md
  memories/repo/**/*.md

REPO-ROOT DISCOVERY:
  The script walks up from its own location looking for the parent that
  contains both `AGENTS.md` AND `.agents/skills/`. That parent is treated
  as repo root; all --scope globs resolve relative to it.

SAFETY:
  - LITERAL string replacement only (no regex). Per §5.1, "renames" are
    always literal-form changes; regex would expand the failure surface.
  - --apply mutates files in place. Run dry-run first; read the diff;
    only then re-invoke with --apply.
  - Files inside `.git/`, `node_modules/`, `__pycache__/`, `.venv/` are
    skipped unconditionally.
"""
from __future__ import annotations

import argparse
import fnmatch
import sys
from pathlib import Path

DEFAULT_SCOPES = [
    ".agents/skills/**/*.md",
    ".agents/skills/**/scripts/**/*.py",
    ".agents/skills/**/scripts/**/*.sh",
    ".agents/skills/**/scripts/**/*.ps1",
    "ai-agent-rules/**/*.md",
    "AGENTS.md",
    "memories/repo/**/*.md",
]

EXCLUDED_DIR_NAMES = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache", ".pytest_cache"}


def find_repo_root(start: Path) -> Path:
    p = start.resolve()
    for ancestor in (p, *p.parents):
        if (ancestor / "AGENTS.md").is_file() and (ancestor / ".agents" / "skills").is_dir():
            return ancestor
    sys.exit(f"FATAL: could not find repo root (AGENTS.md + .agents/skills/) above {start}")


def iter_files(root: Path, scopes: list[str]):
    seen: set[Path] = set()
    for scope in scopes:
        for path in root.glob(scope):
            if not path.is_file():
                continue
            if any(part in EXCLUDED_DIR_NAMES for part in path.relative_to(root).parts):
                continue
            if path in seen:
                continue
            seen.add(path)
            yield path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old", required=True, help="Literal string to find (no regex).")
    ap.add_argument("--new", required=True, help="Literal replacement string.")
    ap.add_argument(
        "--scope",
        action="append",
        default=None,
        help="Glob (relative to repo root). Repeatable. Defaults documented in --help.",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Mutate files in place. Without this flag, only dry-run preview is printed.",
    )
    ap.add_argument(
        "--repo-root",
        default=None,
        help="Override repo-root auto-discovery (must contain AGENTS.md + .agents/skills/).",
    )
    args = ap.parse_args()

    if args.old == args.new:
        sys.exit("FATAL: --old and --new are identical; nothing to sweep.")
    if not args.old:
        sys.exit("FATAL: --old must be non-empty.")

    here = Path(__file__).resolve()
    root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root(here)
    scopes = args.scope if args.scope else DEFAULT_SCOPES

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[post-rename-sweep] mode={mode}  root={root}")
    print(f"[post-rename-sweep] old={args.old!r}  new={args.new!r}")
    print(f"[post-rename-sweep] scopes={scopes}")
    print()

    total_files_with_hits = 0
    total_hit_count = 0
    mutated_files = 0

    for path in sorted(iter_files(root, scopes)):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        count = text.count(args.old)
        if count == 0:
            continue
        total_files_with_hits += 1
        total_hit_count += count
        rel = path.relative_to(root)
        print(f"  {rel}: {count} hit(s)")
        if args.apply:
            new_text = text.replace(args.old, args.new)
            path.write_text(new_text, encoding="utf-8")
            mutated_files += 1

    print()
    print(f"[post-rename-sweep] files-with-hits={total_files_with_hits}  total-hits={total_hit_count}")
    if args.apply:
        print(f"[post-rename-sweep] mutated={mutated_files}  (re-run WITHOUT --apply to verify zero residuals)")
        return 0
    if total_hit_count == 0:
        print("[post-rename-sweep] no residual hits — clean.")
        return 0
    print("[post-rename-sweep] dry-run: review hits above; re-run with --apply to mutate.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
