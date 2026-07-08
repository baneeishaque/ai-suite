#!/usr/bin/env python3
"""
Text Block Indent Override (Base Primitive)

Generic, language-agnostic primitive that locates a delimited text block by regex
and re-indents specific lines inside it from N spaces to M spaces.

Domain-agnostic: NO knowledge of JSON, YAML, TOML, or any specific config syntax.
Composer skills (e.g. json-block-indent-override) supply the block-pattern.

CLI contract (stable):
    --file              Path to input file
    --block-pattern     Regex matching the entire block (use DOTALL semantics)
    --from-spaces N     Current leading-space count to match
    --to-spaces   M     Replacement leading-space count
    --target-line-prefix STR ...  Optional: only rewrite lines whose content after
                                  the from-spaces prefix starts with one of these
    --dry-run           Print the rewritten block(s) without saving
    --no-backup         Skip .bak creation (default: backup is created)

Exit codes:
    0 — success (or dry-run completed)
    1 — pattern not found / IO error / invalid args
"""

import argparse
import re
import shutil
import sys
from typing import List, Optional


def rewrite_block(
    file_path: str,
    block_pattern: str,
    from_spaces: int,
    to_spaces: int,
    target_line_prefixes: Optional[List[str]] = None,
    dry_run: bool = False,
    no_backup: bool = False,
) -> None:
    with open(file_path, encoding="utf-8") as f:
        text = f.read()

    from_prefix = " " * from_spaces
    to_prefix = " " * to_spaces

    def reindent(m: re.Match) -> str:
        block = m.group(0)
        lines = block.split("\n")
        result = []
        for i, line in enumerate(lines):
            # Skip the opening and closing delimiter lines
            if i == 0 or i == len(lines) - 1:
                result.append(line)
                continue
            if line.startswith(from_prefix):
                stripped = line[from_spaces:]
                if target_line_prefixes:
                    if any(stripped.startswith(p) for p in target_line_prefixes):
                        line = to_prefix + stripped
                else:
                    line = to_prefix + stripped
            result.append(line)
        return "\n".join(result)

    try:
        new_text, count = re.subn(
            block_pattern, reindent, text, flags=re.DOTALL
        )
    except re.error as e:
        print(f"Error: invalid --block-pattern regex: {e}", file=sys.stderr)
        sys.exit(1)

    if count == 0:
        print(
            f"Error: --block-pattern matched 0 blocks in {file_path}.",
            file=sys.stderr,
        )
        sys.exit(1)

    if dry_run:
        for m in re.finditer(block_pattern, new_text, flags=re.DOTALL):
            print(m.group(0)[:1500])
            print("---")
        return

    if not no_backup:
        shutil.copy2(file_path, f"{file_path}.bak")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(
        f"Rewrote {count} block(s) in {file_path} "
        f"({from_spaces}sp -> {to_spaces}sp)."
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Base primitive: re-indent specific lines inside a regex-matched "
            "text block. Domain-agnostic."
        )
    )
    parser.add_argument("--file", required=True)
    parser.add_argument(
        "--block-pattern",
        required=True,
        help="Regex matching the full block (DOTALL applied).",
    )
    parser.add_argument("--from-spaces", type=int, required=True)
    parser.add_argument("--to-spaces", type=int, required=True)
    parser.add_argument(
        "--target-line-prefix",
        nargs="+",
        help=(
            "Optional: only rewrite lines whose content (after the from-spaces "
            "prefix) starts with one of these literal strings."
        ),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    args = parser.parse_args()

    rewrite_block(
        args.file,
        args.block_pattern,
        args.from_spaces,
        args.to_spaces,
        args.target_line_prefix,
        args.dry_run,
        args.no_backup,
    )


if __name__ == "__main__":
    main()
