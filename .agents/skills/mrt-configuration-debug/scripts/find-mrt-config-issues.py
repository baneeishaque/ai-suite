"""
find-mrt-config-issues.py — Scan MRT Table*.tsx files for enable* config props.

Usage:
    python3 find-mrt-config-issues.py --glob "src/Pages/**/Table*.tsx"

Outputs a markdown table listing each file and the known enable* props set to
false or true. Unknown/missing props are shown as "—".
"""

import argparse
import json
import re
import sys
from pathlib import Path

KNOWN_PROPS = [
    "enableDensityToggle",
    "enableFullScreenToggle",
    "enableColumnFilters",
    "enableHiding",
    "enableGlobalFilter",
    "enableRowSelection",
    "enableGrouping",
    "enableColumnOrdering",
]

PROP_RE = re.compile(r"^\s*(enable\w+)\s*:\s*(true|false)", re.MULTILINE)


def find_config_issues(glob_pattern: str, base_dir: Path) -> list[dict]:
    results = []
    files = sorted(base_dir.glob(glob_pattern))
    if not files:
        print(f"Warning: no files matched pattern '{glob_pattern}' in {base_dir}",
              file=sys.stderr)
        return results

    for filepath in files:
        try:
            text = filepath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: cannot read {filepath}: {e}", file=sys.stderr)
            continue

        rel_path = filepath.relative_to(base_dir)
        props_found = {p: None for p in KNOWN_PROPS}
        for match in PROP_RE.finditer(text):
            name = match.group(1)
            value = match.group(2)
            if name in props_found:
                props_found[name] = value

        results.append({
            "file": str(rel_path),
            "props": props_found,
        })

    return results


def print_markdown_table(results: list[dict]) -> None:
    if not results:
        print("(no results)")
        return

    header = "| File | " + " | ".join(KNOWN_PROPS) + " |"
    sep = "| :--- " + " | :--- " * len(KNOWN_PROPS) + " |"
    print(header)
    print(sep)

    for r in results:
        row = f"| `{r['file']}` "
        for p in KNOWN_PROPS:
            v = r["props"].get(p)
            if v is None:
                row += "| — "
            elif v == "true":
                row += "| ✅ "
            else:
                row += "| ❌ "
        row += "|"
        print(row)


def print_json(results: list[dict]) -> None:
    print(json.dumps(results, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan MRT Table*.tsx files for enable* config props"
    )
    parser.add_argument(
        "--glob",
        default="src/Pages/**/Table*.tsx",
        help="Glob pattern for table files (default: src/Pages/**/Table*.tsx)",
    )
    parser.add_argument(
        "--base",
        type=Path,
        default=Path.cwd(),
        help="Base directory to search from (default: current working dir)",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    args = parser.parse_args()

    results = find_config_issues(args.glob, args.base)

    if args.format == "json":
        print_json(results)
    else:
        print_markdown_table(results)

    # Exit code: 0 if any issues found, 1 if none
    issues_found = any(
        v == "false"
        for r in results
        for v in r["props"].values()
        if v is not None
    )
    sys.exit(0 if issues_found else 1)


if __name__ == "__main__":
    main()
