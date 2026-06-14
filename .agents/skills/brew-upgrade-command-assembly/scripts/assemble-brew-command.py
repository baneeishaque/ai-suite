#!/usr/bin/env python3
"""
Assemble Homebrew upgrade commands from package lists.

Generic primitive for building brew command chains.
See SKILL.md for the full CLI contract.
"""

import argparse
import sys


def assemble_command(
    formula_names: list[str],
    cask_names: list[str],
    fetch_only: list[str],
) -> str:
    """Assemble a single-line brew upgrade command chain.

    The output follows this structure:
      export HOMEBREW_DOWNLOAD_CONCURRENCY=1;
        brew upgrade --verbose --formula <f1> && brew cleanup --verbose <f1> &&
        brew upgrade --verbose --cask <c1> && brew cleanup --verbose <c1> &&
        brew cleanup --prune=all --verbose &&
        brew fetch --cask --verbose <fetch1> && ...
    """
    parts = ["export HOMEBREW_DOWNLOAD_CONCURRENCY=1;"]

    for pkg in formula_names:
        parts.append(f"brew upgrade --verbose --formula {pkg}")
        parts.append(f"brew cleanup --verbose {pkg}")

    for pkg in cask_names:
        parts.append(f"brew upgrade --verbose --cask {pkg}")
        parts.append(f"brew cleanup --verbose {pkg}")

    parts.append("brew cleanup --prune=all --verbose")

    for pkg in fetch_only:
        parts.append(f"brew fetch --cask --verbose {pkg}")

    return " && ".join(parts)


def parse_stdin_lines() -> tuple[list[str], list[str], list[str]]:
    """Parse newline-separated lines from stdin with type prefixes.

    Accepted prefixes:
      formula:<name>   -> formula_names
      cask:<name>      -> cask_names
      fetch:<name>     -> fetch_only
      <name>           -> cask_names (default, no prefix)
    """
    formula_names: list[str] = []
    cask_names: list[str] = []
    fetch_only: list[str] = []

    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if ":" in line:
            prefix, name = line.split(":", 1)
            name = name.strip()
            if not name:
                continue
            if prefix.strip() == "formula":
                formula_names.append(name)
            elif prefix.strip() == "fetch":
                fetch_only.append(name)
            else:
                cask_names.append(name)
        else:
            cask_names.append(line)

    return formula_names, cask_names, fetch_only


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assemble Homebrew upgrade command chain from package lists",
    )
    parser.add_argument(
        "--formula-names",
        type=str,
        default="",
        help="Comma-separated formula names",
    )
    parser.add_argument(
        "--cask-names",
        type=str,
        default="",
        help="Comma-separated cask names",
    )
    parser.add_argument(
        "--fetch-only",
        type=str,
        default="",
        help="Comma-separated casks to download only (appended after --prune=all)",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read newline-separated package entries from stdin "
        "(prefix with formula:/cask:/fetch: to control placement)",
    )

    args = parser.parse_args()

    if args.stdin:
        formula_names, cask_names, fetch_only = parse_stdin_lines()
    else:
        formula_names = [p.strip() for p in args.formula_names.split(",") if p.strip()]
        cask_names = [p.strip() for p in args.cask_names.split(",") if p.strip()]
        fetch_only = [p.strip() for p in args.fetch_only.split(",") if p.strip()]

    if not formula_names and not cask_names and not fetch_only:
        print("Error: no packages specified", file=sys.stderr)
        return 1

    result = assemble_command(formula_names, cask_names, fetch_only)
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
