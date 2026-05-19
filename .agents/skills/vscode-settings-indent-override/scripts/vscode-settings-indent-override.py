#!/usr/bin/env python3
"""
VS Code Settings Indent Override (Composer over json-block-indent-override)

Thin wrapper that adds VS Code-specific affordances on top of the JSON composer:
known canonical paths to settings.json across Stable / Insiders / profiles,
post-write JSON-validity reporting, and (via documentation) the post-promotion
workflow.

Shells out to: ../../json-block-indent-override/scripts/json-block-indent-override.py
"""

import argparse
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_COMPOSER = os.path.normpath(
    os.path.join(
        SCRIPT_DIR,
        "..",
        "..",
        "json-block-indent-override",
        "scripts",
        "json-block-indent-override.py",
    )
)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Apply per-key indent overrides to a VS Code settings.json by "
            "composing the json-block-indent-override skill."
        )
    )
    parser.add_argument("--file", required=True, help="Path to settings.json")
    parser.add_argument(
        "--key", required=True, help="Top-level JSON key, e.g. files.associations"
    )
    parser.add_argument("--from-spaces", type=int, required=True)
    parser.add_argument("--to-spaces", type=int, required=True)
    parser.add_argument("--target-keys", nargs="+")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(JSON_COMPOSER):
        print(
            f"Error: json composer not found: {JSON_COMPOSER}\n"
            "Ensure json-block-indent-override is installed alongside this skill.",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = [
        sys.executable,
        JSON_COMPOSER,
        "--file", args.file,
        "--key", args.key,
        "--from-spaces", str(args.from_spaces),
        "--to-spaces", str(args.to_spaces),
    ]
    if args.target_keys:
        cmd += ["--target-keys", *args.target_keys]
    if args.dry_run:
        cmd.append("--dry-run")

    sys.exit(subprocess.run(cmd).returncode)


if __name__ == "__main__":
    main()
