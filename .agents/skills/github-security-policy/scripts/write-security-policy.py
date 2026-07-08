#!/usr/bin/env python3
"""Generate a SECURITY.md for a GitHub repository."""

import argparse
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "SECURITY.md.template"

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a SECURITY.md")
    parser.add_argument("--email", default="security@example.com", help="Security contact email")
    parser.add_argument("--latest-version", default="latest", help="Latest supported version")
    parser.add_argument("--acknowledgement-hours", default="48", help="Acknowledgement window in hours")
    parser.add_argument("--output", default="SECURITY.md", help="Output file path")
    args = parser.parse_args()

    older_versions = "Older versions are not supported." if args.latest_version == "latest" else f"Versions prior to {args.latest_version} are not supported."
    content = (
        TEMPLATE_PATH.read_text()
        .replace("{latest_version}", args.latest_version)
        .replace("{email}", args.email)
        .replace("{acknowledgement_hours}", args.acknowledgement_hours)
        .replace("{older_versions_statement}", older_versions)
    )
    if args.output == "-":
        sys.stdout.write(content)
    else:
        with open(args.output, "w") as f:
            f.write(content)
        print(f"Wrote {args.output}", file=sys.stderr)

if __name__ == "__main__":
    main()
