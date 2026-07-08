"""
scan-reset-mocks-vulnerabilities.py

Scan test files for three vulnerability patterns caused by CRA's
resetMocks: true default:

1. jest.fn() inside jest.mock factories — implementations get stripped
2. Direct variable capture in jest.mock factories — captures undefined
   at hoist time (TDZ issue)
3. jest.fn() inside objects returned by jest.mock factories

Usage:
  python3 scan-reset-mocks-vulnerabilities.py --file <path>
  python3 scan-reset-mocks-vulnerabilities.py --glob "<glob-pattern>"
  python3 scan-reset-mocks-vulnerabilities.py --file <path> --format json
"""

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any


VULNERABILITY_PATTERNS = {
    "jest.fn in jest.mock factory": re.compile(
        r'jest\.mock\s*\([^)]+\)\s*,\s*\([^)]*\)\s*=>\s*\{[^}]*jest\.fn\s*\(',
        re.DOTALL,
    ),
    "direct var capture in jest.mock": re.compile(
        r'jest\.mock\s*\([^)]+\)\s*,\s*\([^)]*\)\s*=>\s*\(\s*\{[^}]*?\b(\w+)\s*:\s*(\w[\w.]*)\b[^}]*\}\s*\)',
        re.DOTALL,
    ),
    "jest.fn in returned object": re.compile(
        r'\b(\w+)\s*:\s*jest\.fn\s*\(',
    ),
}

SAFE_PATTERNS = {
    "wrapper function": re.compile(r'\b(\w+)\s*:\s*\(\.\.\.args\)\s*=>\s*\w+\(\.\.\.args\)'),
    "arrow function body": re.compile(r'\b(\w+)\s*:\s*\([^)]*\)\s*=>\s*\{'),
    "plain arrow": re.compile(r'\b(\w+)\s*:\s*\([^)]*\)\s*=>\s*\('),
}


def scan_file(filepath: str) -> Dict[str, Any]:
    path = Path(filepath)
    if not path.exists():
        return {"file": filepath, "error": "File not found", "vulnerabilities": []}

    content = path.read_text(encoding="utf-8", errors="replace")
    results = []

    for vuln_name, pattern in VULNERABILITY_PATTERNS.items():
        for match in pattern.finditer(content):
            start = max(0, match.start() - 40)
            end = min(len(content), match.end() + 40)
            context = content[start:end].replace("\n", "\\n")

            # Check if this match is actually safe (false positive reduction)
            if _is_safe_pattern(content, match):
                continue

            results.append({
                "type": vuln_name,
                "pos": match.start(),
                "match": match.group(0)[:120],
                "context": context,
            })

    return {"file": filepath, "vulnerabilities": results}


def _is_safe_pattern(content: str, match: re.Match) -> bool:
    """Check if a match is mitigated by an adjacent safe pattern."""
    match_start = match.start()
    match_end = match.end()
    window = content[max(0, match_start - 200) : min(len(content), match_end + 200)]

    for _, pattern in SAFE_PATTERNS.items():
        if pattern.search(window):
            return True
    return False


def scan_glob(pattern: str) -> List[Dict[str, Any]]:
    import glob as glob_module
    paths = glob_module.glob(pattern, recursive=True)
    results = []
    for p in paths:
        if os.path.isfile(p):
            results.append(scan_file(p))
    return results


def format_text(results: List[Dict[str, Any]]) -> str:
    lines = []
    total_vulns = 0
    for r in results:
        if r.get("error"):
            lines.append(f"[ERR] {r['file']}: {r['error']}")
            continue
        vulns = r.get("vulnerabilities", [])
        if not vulns:
            lines.append(f"[OK]  {r['file']} — no vulnerabilities found")
            continue
        total_vulns += len(vulns)
        lines.append(f"[VULN] {r['file']} — {len(vulns)} issue(s):")
        for v in vulns:
            lines.append(f"  Line ~{v['pos']}: [{v['type']}]")
            lines.append(f"    Match: {v['match'][:100]}")
    lines.append(f"\nTotal: {total_vulns} vulnerabilities across {len(results)} file(s)")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Scan test files for CRA resetMocks vulnerability patterns"
    )
    parser.add_argument("--file", type=str, help="Path to a single test file")
    parser.add_argument("--glob", type=str, help="Glob pattern for test files")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if not args.file and not args.glob:
        parser.print_help()
        sys.exit(2)

    results = []
    if args.file:
        results.append(scan_file(args.file))
    elif args.glob:
        results = scan_glob(args.glob)

    total_vulns = sum(len(r.get("vulnerabilities", [])) for r in results)
    exit_code = 1 if total_vulns > 0 else 0

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
