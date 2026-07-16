#!/usr/bin/env python3
"""Generate a SUPPORT.md for a GitHub repository."""

import argparse
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "SUPPORT.md.template"

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a SUPPORT.md")
    parser.add_argument("--owner", default="owner", help="Repository owner")
    parser.add_argument("--repo-name", default="repo", help="Repository name")
    parser.add_argument("--security-email", default="security@example.com", help="Security contact email")
    parser.add_argument("--output", default="SUPPORT.md", help="Output file path")
    args = parser.parse_args()

    docs = "See the `docs/` directory for detailed documentation."
    discussions = f"https://github.com/{args.owner}/{args.repo_name}/discussions"
    commercial = "Not currently available."

    content = (
        TEMPLATE_PATH.read_text()
        .replace("{repo_name}", args.repo_name)
        .replace("{owner}", args.owner)
        .replace("{security_email}", args.security_email)
        .replace("{docs_link}", docs)
        .replace("{discussions_link}", discussions)
        .replace("{commercial_support_statement}", commercial)
    )
    if args.output == "-":
        sys.stdout.write(content)
    else:
        with open(args.output, "w") as f:
            f.write(content)
        print(f"Wrote {args.output}", file=sys.stderr)

if __name__ == "__main__":
    main()
