#!/usr/bin/env python3
"""Generate a CONTRIBUTING.md for a GitHub repository."""

import argparse
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "CONTRIBUTING.md.template"

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a CONTRIBUTING.md")
    parser.add_argument("--owner", default="owner", help="Repository owner")
    parser.add_argument("--repo-name", default="repo", help="Repository name")
    parser.add_argument("--setup-instructions", default="1. Install Python 3.12+\n2. Install dependencies: `pip install -r requirements.txt`", help="Development setup instructions")
    parser.add_argument("--code-style-instructions", default="Follow PEP 8. Run `ruff check .` before committing.", help="Code style guidelines")
    parser.add_argument("--output", default="CONTRIBUTING.md", help="Output file path")
    args = parser.parse_args()

    content = (
        TEMPLATE_PATH.read_text()
        .replace("{repo_name}", args.repo_name)
        .replace("{owner}", args.owner)
        .replace("{setup_instructions}", args.setup_instructions)
        .replace("{code_style_instructions}", args.code_style_instructions)
    )
    if args.output == "-":
        sys.stdout.write(content)
    else:
        with open(args.output, "w") as f:
            f.write(content)
        print(f"Wrote {args.output}", file=sys.stderr)

if __name__ == "__main__":
    main()
