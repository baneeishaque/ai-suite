#!/usr/bin/env python3
"""Create the standard repository skeleton for a GitHub project.

Creates: .github/workflows/, .github/ISSUE_TEMPLATE/, scripts/, docs/.
"""
import argparse
import json
import sys
from pathlib import Path

REPO_DIRS = [
    ".github/workflows",
    ".github/ISSUE_TEMPLATE",
    "scripts",
    "docs",
]

def main() -> None:
    parser = argparse.ArgumentParser(description="Create repository folder structure")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument("--include-docs", action="store_true", help="Also create docs/ subdirs")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be created without writing")
    args = parser.parse_args()

    root = Path(args.repo_root)
    created = []

    dirs = REPO_DIRS.copy()
    if args.include_docs:
        dirs.extend(["docs/architecture", "docs/decisions", "docs/implementation-plans", "docs/guides"])

    for rel_dir in dirs:
        target = root / rel_dir
        if args.dry_run:
            print(f"mkdir -p {target}")
        else:
            target.mkdir(parents=True, exist_ok=True)
            gitkeep = target / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.write_text("")
            created.append(str(target))
            print(f"Created {target}", file=sys.stderr)

    if not args.dry_run:
        print(json.dumps({"created": created}), file=sys.stderr)

if __name__ == "__main__":
    main()
