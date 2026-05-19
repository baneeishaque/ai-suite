#!/usr/bin/env python3
"""
JSON Block Indent Override (Composer over text-block-indent-override)

Re-indents lines inside a top-level JSON key's block. Builds the JSON-shaped
block pattern from --key, auto-quotes --target-keys, validates the result with
json.loads, and rolls back on parse failure.

Shells out to the base skill: ../../text-block-indent-override/scripts/text-block-indent-override.py
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from typing import List, Optional


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_SCRIPT = os.path.normpath(
    os.path.join(
        SCRIPT_DIR,
        "..",
        "..",
        "text-block-indent-override",
        "scripts",
        "text-block-indent-override.py",
    )
)


def apply(
    file_path: str,
    key: str,
    from_spaces: int,
    to_spaces: int,
    target_keys: Optional[List[str]] = None,
    dry_run: bool = False,
) -> None:
    if not os.path.exists(BASE_SCRIPT):
        print(
            f"Error: base script not found: {BASE_SCRIPT}\n"
            "Ensure text-block-indent-override is installed alongside this skill.",
            file=sys.stderr,
        )
        sys.exit(1)

    # JSON-shaped block pattern: "key": { ... \n}
    # Allows for the closing brace at any leading-space depth (nested or top-level).
    escaped = re.escape(key)
    block_pattern = rf'"{escaped}":\s*\{{.*?\n[ \t]*\}}'

    # Wrap target keys in double quotes for the base's literal prefix matching
    target_line_prefixes = (
        [f'"{k}"' for k in target_keys] if target_keys else None
    )

    cmd = [
        sys.executable,
        BASE_SCRIPT,
        "--file", file_path,
        "--block-pattern", block_pattern,
        "--from-spaces", str(from_spaces),
        "--to-spaces", str(to_spaces),
        "--no-backup",  # composer creates its own backup so it can roll back
    ]
    if target_line_prefixes:
        cmd += ["--target-line-prefix", *target_line_prefixes]
    if dry_run:
        cmd.append("--dry-run")

    if dry_run:
        # In dry-run, base prints the rewritten block — pass through and exit
        result = subprocess.run(cmd)
        sys.exit(result.returncode)

    # Composer-owned backup for rollback on JSON validation failure
    bak = f"{file_path}.bak"
    shutil.copy2(file_path, bak)

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(
            f"Base script failed (exit {result.returncode}); leaving file untouched.",
            file=sys.stderr,
        )
        # Base script ran with --no-backup AND we never saw a successful write,
        # but to be safe restore from our own .bak.
        shutil.copy2(bak, file_path)
        sys.exit(result.returncode)

    # Post-write JSON validation
    try:
        with open(file_path, encoding="utf-8") as f:
            json.load(f)
    except json.JSONDecodeError as e:
        print(
            f"JSON validation FAILED after rewrite: {e}\n"
            f"Rolling back to {bak}.",
            file=sys.stderr,
        )
        shutil.copy2(bak, file_path)
        sys.exit(1)

    print(
        f"JSON validation passed. Indent override applied to '{key}' "
        f"({from_spaces}sp -> {to_spaces}sp). Backup: {bak}"
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Composer over text-block-indent-override: re-indent lines inside a "
            "top-level JSON key's block with auto-quoting and json.loads validation."
        )
    )
    parser.add_argument("--file", required=True, help="Path to JSON file")
    parser.add_argument("--key", required=True, help="Top-level JSON key")
    parser.add_argument("--from-spaces", type=int, required=True)
    parser.add_argument("--to-spaces", type=int, required=True)
    parser.add_argument(
        "--target-keys",
        nargs="+",
        help=(
            "Optional: only re-indent lines whose sub-key matches one of these. "
            "Composer auto-wraps each in double quotes."
        ),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    apply(
        args.file,
        args.key,
        args.from_spaces,
        args.to_spaces,
        args.target_keys,
        args.dry_run,
    )


if __name__ == "__main__":
    main()
