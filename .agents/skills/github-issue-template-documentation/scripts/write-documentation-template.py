#!/usr/bin/env python3
"""Write `.github/ISSUE_TEMPLATE/documentation.yml` — Documentation Request."""

import argparse
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "documentation.yml.template"

def main() -> int:
    parser = argparse.ArgumentParser(description="Write GitHub documentation template")
    parser.add_argument("--repo-root", default=".", help="Path to repository root (default: .)")
    args = parser.parse_args()
    dest = Path(args.repo_root) / ".github" / "ISSUE_TEMPLATE" / "documentation.yml"
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(TEMPLATE_PATH.read_text())
        print(f"Wrote documentation template to {dest}")
        return 0
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
