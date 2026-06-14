#!/usr/bin/env python3
"""
Homebrew upgrade workflow orchestrator.

Discovers outdated leaves, resolves formula vs cask types,
applies priority ordering, and delegates command assembly
to the base primitive.

See SKILL.md for the full CLI contract.
"""

import argparse
import csv
import io
import os
import subprocess
import sys
import shlex

DEFAULT_PRIORITY = [
    "google-chrome",
    "onedrive",
    "visual-studio-code",
    "visual-studio-code-insiders",
    "gemini-cli",
]

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
ASSEMBLER_SCRIPT = os.path.join(
    SKILL_DIR, "..", "brew-upgrade-command-assembly", "scripts", "assemble-brew-command.py",
)


def run_brew(args: list[str], debug: bool = False) -> str:
    """Run a brew command and return stdout. Raises on failure."""
    cmd = ["brew"] + args
    if debug:
        print(f"[debug] Running: {' '.join(shlex.quote(a) for a in cmd)}", file=sys.stderr)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running 'brew {' '.join(args)}': {e.stderr.strip()}", file=sys.stderr)
        raise


def parse_outdated(output: str) -> set[str]:
    """Parse 'brew outdated --greedy' output into a set of package names."""
    packages = set()
    for line in output.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Format: "package-name (current) < latest" or "package-name (latest) < current"
        pkg = line.split(" ")[0]
        packages.add(pkg)
    return packages


def get_leaves(debug: bool = False) -> set[str]:
    """Get explicitly installed formulae via 'brew leaves --installed-on-request'."""
    output = run_brew(["leaves", "--installed-on-request"], debug=debug)
    return set(line.strip() for line in output.strip().splitlines() if line.strip())


def get_casks(debug: bool = False) -> set[str]:
    """Get installed casks."""
    output = run_brew(["list", "--cask"], debug=debug)
    return set(line.strip() for line in output.strip().splitlines() if line.strip())


def get_formulae(debug: bool = False) -> set[str]:
    """Get installed formulae."""
    output = run_brew(["list", "--formula"], debug=debug)
    return set(line.strip() for line in output.strip().splitlines() if line.strip())


def resolve_type(
    pkg: str,
    casks: set[str],
    formulae: set[str],
    debug: bool = False,
) -> str:
    """Resolve a package as 'formula' or 'cask'.

    Checks installed lists first, then falls back to 'brew info'.
    """
    if pkg in formulae and pkg not in casks:
        return "formula"
    if pkg in casks and pkg not in formulae:
        return "cask"
    # Ambiguous or unknown — query brew info
    if pkg in casks and pkg in formulae:
        # Both lists contain it — probably a cask with same name as a formula
        return "cask"
    return "cask"


def apply_priority(
    packages: set[str],
    user_priority: list[str],
    debug: bool = False,
) -> list[str]:
    """Sort packages by priority.

    Order:
      1. User-specified priority packages (in given order)
      2. Default priority packages (in default order)
      3. Remaining packages (alphabetical)

    Returns a list of (package_name, priority_group) for debugging.
    """
    ordered: list[str] = []
    remaining = set(packages)

    # 1. User priority
    for pkg in user_priority:
        if pkg in remaining:
            ordered.append(pkg)
            remaining.remove(pkg)

    # 2. Default priority
    for pkg in DEFAULT_PRIORITY:
        if pkg in remaining:
            ordered.append(pkg)
            remaining.remove(pkg)

    # 3. Remaining alphabetical
    ordered.extend(sorted(remaining))

    if debug:
        print(f"[debug] Priority order: {ordered}", file=sys.stderr)

    return ordered


def assemble_command(
    formula_names: list[str],
    cask_names: list[str],
    fetch_only: list[str],
    assembler_path: str = ASSEMBLER_SCRIPT,
) -> str:
    """Invoke the base primitive and return the assembled command."""
    cmd = [
        sys.executable,
        assembler_path,
        "--formula-names", ",".join(formula_names),
        "--cask-names", ",".join(cask_names),
        "--fetch-only", ",".join(fetch_only),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error in assembler: {e.stderr.strip()}", file=sys.stderr)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Homebrew upgrade workflow — discover outdated leaves, resolve types, assemble command",
    )
    parser.add_argument(
        "--only",
        type=str,
        default="",
        help="Comma-separated — only upgrade these packages",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        default="",
        help="Comma-separated — skip these packages",
    )
    parser.add_argument(
        "--fetch-only",
        type=str,
        default="",
        help="Comma-separated — download these casks without installing",
    )
    parser.add_argument(
        "--priority",
        type=str,
        default="",
        help="Comma-separated — order these packages first (default priority applied to rest)",
    )
    parser.add_argument(
        "--outfile",
        type=str,
        default="",
        help="Write the final command to this file instead of stdout",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print intermediate discovery state to stderr",
    )

    args = parser.parse_args()

    only_list = [p.strip() for p in args.only.split(",") if p.strip()]
    exclude_list = [p.strip() for p in args.exclude.split(",") if p.strip()]
    fetch_only_list = [p.strip() for p in args.fetch_only.split(",") if p.strip()]
    priority_list = [p.strip() for p in args.priority.split(",") if p.strip()]

    # Step 1: Discover outdated packages
    if args.debug:
        print("[debug] Step 1: Discovering outdated packages...", file=sys.stderr)
    try:
        outdated_output = run_brew(["outdated", "--greedy"], debug=args.debug)
    except subprocess.CalledProcessError:
        return 2
    outdated = parse_outdated(outdated_output)

    if not outdated:
        print("No outdated packages found.", file=sys.stderr)
        return 1

    if args.debug:
        print(f"[debug] Outdated ({len(outdated)}): {sorted(outdated)}", file=sys.stderr)

    # Step 2: If --only specified, restrict to those
    if only_list:
        outdated &= set(only_list)
        if args.debug:
            print(f"[debug] After --only filter ({len(outdated)}): {sorted(outdated)}", file=sys.stderr)

    # Step 3: Remove exclusions
    if exclude_list:
        outdated -= set(exclude_list)
        if args.debug:
            print(f"[debug] After --exclude filter ({len(outdated)}): {sorted(outdated)}", file=sys.stderr)

    if not outdated:
        print("All outdated packages were excluded. Nothing to upgrade.", file=sys.stderr)
        return 1

    # Step 4: Get leaves (explicitly installed formulae)
    leaves = get_leaves(debug=args.debug)
    casks = get_casks(debug=args.debug)
    formulae = get_formulae(debug=args.debug)

    # Step 5: Filter to leaves only (formulae that are leaves, plus all casks)
    filtered: set[str] = set()
    for pkg in outdated:
        if pkg in casks:
            filtered.add(pkg)
        elif pkg in leaves:
            filtered.add(pkg)
        elif pkg in formulae and pkg not in leaves:
            # Dependency formula — skip with warning
            print(
                f"[warn] Skipping '{pkg}' — it is a dependency formula, not a leaf. "
                f"Use --only to force-upgrade it.",
                file=sys.stderr,
            )
        else:
            # Unknown — include as cask default
            filtered.add(pkg)

    if args.debug:
        print(f"[debug] After leaf filter ({len(filtered)}): {sorted(filtered)}", file=sys.stderr)

    if not filtered:
        print("No outdated leaves found (all outdated packages are dependencies).", file=sys.stderr)
        return 1

    # Step 6: Resolve formula vs cask for each package
    resolved_formulae: list[str] = []
    resolved_casks: list[str] = []
    for pkg in apply_priority(filtered, priority_list, debug=args.debug):
        pkg_type = resolve_type(pkg, casks, formulae, debug=args.debug)
        if pkg_type == "formula":
            resolved_formulae.append(pkg)
        else:
            resolved_casks.append(pkg)

    if args.debug:
        print(f"[debug] Formulae: {resolved_formulae}", file=sys.stderr)
        print(f"[debug] Casks: {resolved_casks}", file=sys.stderr)
        print(f"[debug] Fetch-only: {fetch_only_list}", file=sys.stderr)

    # Step 7: Assemble the final command
    try:
        command = assemble_command(
            formula_names=resolved_formulae,
            cask_names=resolved_casks,
            fetch_only=fetch_only_list,
        )
    except subprocess.CalledProcessError:
        return 2

    # Step 8: Output
    if args.outfile:
        with open(args.outfile, "w") as f:
            f.write(command + "\n")
        print(f"Command written to: {args.outfile}")
    else:
        print(command)

    return 0


if __name__ == "__main__":
    sys.exit(main())
