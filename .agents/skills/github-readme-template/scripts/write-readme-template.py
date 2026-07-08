#!/usr/bin/env python3
"""Generate a README.md template for a GitHub repository."""

import argparse
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "README.md.template"

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a README.md template")
    parser.add_argument("--repo-name", default="my-repo", help="Repository name")
    parser.add_argument("--description", default="", help="Repository description")
    parser.add_argument("--features", default="- Feature A\n- Feature B\n- Feature C", help="Feature list (use \\n)")
    parser.add_argument("--install-command", default="pip install my-repo", help="Installation command")
    parser.add_argument("--usage-command", default="my-repo --help", help="Usage command")
    parser.add_argument("--license-name", default="MIT", help="License name")
    parser.add_argument("--output", default="README.md", help="Output file path")
    args = parser.parse_args()

    content = (
        TEMPLATE_PATH.read_text()
        .replace("{repo_name}", args.repo_name)
        .replace("{description}", args.description)
        .replace("{features}", args.features)
        .replace("{install_command}", args.install_command)
        .replace("{usage_command}", args.usage_command)
        .replace("{license_name}", args.license_name)
        .replace("{docs_link}", "See the `docs/` directory for detailed documentation.")
    )
    if args.output == "-":
        sys.stdout.write(content)
    else:
        with open(args.output, "w") as f:
            f.write(content)
        print(f"Wrote {args.output}", file=sys.stderr)

if __name__ == "__main__":
    main()
