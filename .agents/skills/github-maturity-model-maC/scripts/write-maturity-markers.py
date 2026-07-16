#!/usr/bin/env python3
"""Add Model as Code (MaC) maturity markers to a GitHub repository's README."""

import argparse
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "maturity-marker.template"

MATURITY_BADGES = {
    "experimental": "![Experimental](https://img.shields.io/badge/maturity-experimental-orange)",
    "beta": "![Beta](https://img.shields.io/badge/maturity-beta-yellow)",
    "stable": "![Stable](https://img.shields.io/badge/maturity-stable-brightgreen)",
    "deprecated": "![Deprecated](https://img.shields.io/badge/maturity-deprecated-red)",
}

def main() -> None:
    parser = argparse.ArgumentParser(description="Add MaC maturity markers to a README")
    parser.add_argument("--maturity", choices=list(MATURITY_BADGES.keys()), default="experimental", help="Project maturity level")
    parser.add_argument("--marker-name", default="maturity", help="MaC marker name")
    parser.add_argument("--output", help="Output file (append). If omitted, prints to stdout.")
    args = parser.parse_args()

    marker = (
        TEMPLATE_PATH.read_text()
        .replace("{marker_name}", args.marker_name)
        .replace("{value}", MATURITY_BADGES[args.maturity])
    )

    if args.output:
        with open(args.output, "a") as f:
            f.write("\n" + marker)
        print(f"Appended MaC marker to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(marker)

if __name__ == "__main__":
    main()
