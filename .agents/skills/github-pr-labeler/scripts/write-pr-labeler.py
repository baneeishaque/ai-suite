#!/usr/bin/env python3
"""Write pr-labeler.yml workflow and labeler-config.yml."""

import argparse
import shutil
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

def main() -> int:
    parser = argparse.ArgumentParser(description="Write PR labeler files")
    parser.add_argument("--repo-root", default=".", help="Path to repository root (default: .)")
    args = parser.parse_args()

    out_dir = Path(args.repo_root) / ".github"
    out_dir.mkdir(parents=True, exist_ok=True)

    workflow_path = out_dir / "workflows" / "pr-labeler.yml"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SCRIPTS_DIR / "pr-labeler-workflow.yml.template", workflow_path)

    config_path = out_dir / "labeler-config.yml"
    shutil.copy2(SCRIPTS_DIR / "labeler-config.yml.template", config_path)

    print(f"Written {workflow_path}")
    print(f"Written {config_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
