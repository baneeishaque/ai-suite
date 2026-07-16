#!/usr/bin/env python3
"""Read a JSONC file (JSON with // comments and trailing commas) and print valid JSON to stdout.

Usage:
    python3 scripts/read-jsonc.py <file-path>

Exits 0 on success, 1 on failure.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def read_jsonc(file_path: str) -> dict:
    """Read a JSONC file, strip comments and trailing commas, return parsed dict."""
    text = Path(file_path).read_text(encoding="utf-8")

    lines = text.split("\n")
    stripped: list[str] = []
    for line in lines:
        if "//" in line:
            in_string = False
            for i, ch in enumerate(line):
                if ch == '"':
                    in_string = not in_string
                elif ch == "/" and i + 1 < len(line) and line[i + 1] == "/" and not in_string:
                    line = line[:i]
                    break
        stripped.append(line)

    cleaned = "\n".join(stripped)
    cleaned = re.sub(r",(\s*[\]}])", r"\1", cleaned)

    return json.loads(cleaned)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file-path>", file=sys.stderr)
        return 1

    try:
        data = read_jsonc(sys.argv[1])
    except FileNotFoundError:
        print(f"ERROR: file not found: {sys.argv[1]}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSONC: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
