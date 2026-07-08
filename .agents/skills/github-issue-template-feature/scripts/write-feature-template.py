#!/usr/bin/env python3
"""Write `.github/ISSUE_TEMPLATE/feature.yml` — Feature Request template."""

import argparse
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "feature.yml.template"

def main() -> int:
    parser = argparse.ArgumentParser(description="Write GitHub feature template")
    parser.add_argument("--repo-root", default=".", help="Path to repository root (default: .)")
    args = parser.parse_args()
    dest = Path(args.repo_root) / ".github" / "ISSUE_TEMPLATE" / "feature.yml"
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(TEMPLATE_PATH.read_text())
        print(f"Wrote feature template to {dest}")
        return 0
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
