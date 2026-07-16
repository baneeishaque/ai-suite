#!/usr/bin/env python3
"""Write .github/workflows/ci-markdown-lint.yml workflow fragment."""

import argparse
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "markdown-lint-job.yml.template"

def main() -> int:
    parser = argparse.ArgumentParser(description="Write markdown lint CI workflow")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--runner", default="ubuntu-24.04", help="GitHub runner OS")
    args = parser.parse_args()

    content = TEMPLATE_PATH.read_text().replace("{runner}", args.runner)
    out_dir = Path(args.repo_root) / ".github" / "workflows"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ci-markdown-lint.yml"
    out_path.write_text(content)
    print(f"Written {out_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
