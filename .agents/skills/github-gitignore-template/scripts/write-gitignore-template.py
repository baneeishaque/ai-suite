#!/usr/bin/env python3
"""Generate a .gitignore file for a GitHub repository."""

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

TEMPLATE_FILES = {
    "python": "gitignore-python.template",
    "node": "gitignore-node.template",
    "generic": "gitignore-generic.template",
}

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a .gitignore template")
    parser.add_argument("--language", choices=list(TEMPLATE_FILES.keys()), default="generic", help="Project language")
    parser.add_argument("--output", default=".gitignore", help="Output file path")
    args = parser.parse_args()

    content = (SCRIPTS_DIR / TEMPLATE_FILES[args.language]).read_text()
    if args.output == "-":
        sys.stdout.write(content)
    else:
        with open(args.output, "w") as f:
            f.write(content)
        print(f"Wrote {args.output}", file=sys.stderr)

if __name__ == "__main__":
    main()
