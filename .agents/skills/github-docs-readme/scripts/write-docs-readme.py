#!/usr/bin/env python3
"""Generate a docs/README.md for a GitHub repository."""

import argparse
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "docs-README.md.template"

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a docs/README.md")
    parser.add_argument("--project-name", default="project", help="Project name")
    parser.add_argument("--output", default="docs/README.md", help="Output file path")
    args = parser.parse_args()

    content = TEMPLATE_PATH.read_text().replace("{project_name}", args.project_name)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content)
    print(f"Wrote {out}", file=sys.stderr)

if __name__ == "__main__":
    main()
