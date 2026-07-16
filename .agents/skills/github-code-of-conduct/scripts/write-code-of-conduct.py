#!/usr/bin/env python3
"""Generate a CODE_OF_CONDUCT.md for a GitHub repository."""

import argparse
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "CODE_OF_CONDUCT.md.template"

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a CODE_OF_CONDUCT.md")
    parser.add_argument("--output", default="CODE_OF_CONDUCT.md", help="Output file path")
    parser.add_argument("--email", default="maintainers@example.com", help="Contact email")
    args = parser.parse_args()

    content = TEMPLATE_PATH.read_text().replace("{email}", args.email)
    if args.output == "-":
        sys.stdout.write(content)
    else:
        with open(args.output, "w") as f:
            f.write(content)
        print(f"Wrote {args.output}", file=sys.stderr)

if __name__ == "__main__":
    main()
