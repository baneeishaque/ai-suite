#!/usr/bin/env python3
"""verify-symlinks.py — Phase 4 verification for the Tool Config Directory Symlink protocol.

Usage:
  printf "/path/to/symlink1\n/path/to/symlink2" | python3 verify-symlinks.py
  python3 verify-symlinks.py --symlinks-file <path>

Input: one symlink path per line (stdin or file).
Exit codes: 0 all resolve, 1 any broken.
"""

import argparse
import os
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that symlinks resolve to existing targets."
    )
    parser.add_argument(
        "--symlinks-file",
        type=str,
        default=None,
        help="Path to a file with one symlink path per line.",
    )
    return parser.parse_args()


def load_symlinks(path: str | None) -> list[str]:
    if path:
        with open(path, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return [line.strip() for line in sys.stdin if line.strip()]


def main() -> None:
    args = parse_args()
    symlinks = load_symlinks(args.symlinks_file)
    all_ok = True

    for link in symlinks:
        if not os.path.islink(link):
            print(f"BROKEN not-a-link: {link}", file=sys.stderr)
            all_ok = False
            continue
        target = os.readlink(link)
        if os.path.exists(link):
            print(f"OK    {link} → {target}")
        else:
            print(f"BROKEN dangling: {link} → {target}", file=sys.stderr)
            all_ok = False

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
