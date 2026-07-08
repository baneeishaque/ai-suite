#!/usr/bin/env python3
"""Create the standard docs/ directory tree for a GitHub repository.

Creates: docs/architecture/, docs/decisions/, docs/implementation-plans/, docs/guides/.
"""
import argparse
import json
import sys
from pathlib import Path

DOCS_SUBDIRS = [
    "architecture",
    "decisions",
    "implementation-plans",
    "guides",
]

def main() -> None:
    parser = argparse.ArgumentParser(description="Create docs/ directory structure")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be created without writing")
    args = parser.parse_args()

    docs_root = Path(args.repo_root) / "docs"
    created = []

    for subdir in DOCS_SUBDIRS:
        target = docs_root / subdir
        if args.dry_run:
            print(f"mkdir -p {target}")
        else:
            target.mkdir(parents=True, exist_ok=True)
            gitkeep = target / ".gitkeep"
            gitkeep.write_text("")
            created.append(str(target))
            print(f"Created {target}", file=sys.stderr)

    if not args.dry_run:
        print(json.dumps({"created": created}), file=sys.stderr)

if __name__ == "__main__":
    main()
