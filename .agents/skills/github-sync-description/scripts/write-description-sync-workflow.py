#!/usr/bin/env python3
"""Write .github/workflows/sync-description.yml workflow."""

import argparse
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "sync-description.yml.template"

def main() -> int:
    parser = argparse.ArgumentParser(description="Write sync-description workflow")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    args = parser.parse_args()

    out_dir = Path(args.repo_root) / ".github" / "workflows"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "sync-description.yml"
    out_path.write_text(TEMPLATE_PATH.read_text())
    print(f"Written {out_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
