#!/usr/bin/env python3
"""Write .github/workflows/ci-python-lint.yml workflow fragment."""

import argparse
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "python-lint-job.yml.template"

def main() -> int:
    parser = argparse.ArgumentParser(description="Write Python lint CI workflow")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--runner", default="ubuntu-24.04", help="GitHub runner OS")
    parser.add_argument("--python-version", default="3.12", help="Python version")
    parser.add_argument("--target-glob", default=".agents/skills/", help="Target glob for ruff")
    args = parser.parse_args()

    content = (
        TEMPLATE_PATH.read_text()
        .replace("{runner}", args.runner)
        .replace("{python_version}", args.python_version)
        .replace("{target_glob}", args.target_glob)
    )
    out_dir = Path(args.repo_root) / ".github" / "workflows"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ci-python-lint.yml"
    out_path.write_text(content)
    print(f"Written {out_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
