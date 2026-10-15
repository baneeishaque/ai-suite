#!/usr/bin/env python3
"""Read a JSONC file and print valid JSON to stdout — thin wrapper over the
jsonc-cst-util base primitive (CST-aware, comment-preserving parser).

Tier: 1 (Python 3.12+) per ai-agent-rules/scripting-language-selection-rules.md
§2.1 — subprocess orchestration; stdlib only.

Usage:
    python3 scripts/read-jsonc.py <file-path>

The CLI contract is stable for downstream consumers: strict JSON (indent 2) on
stdout; exit 0 on success, 1 on failure with a diagnostic on stderr.

Exit codes:
    0 — success
    1 — failure (missing file, invalid JSONC, or missing base script)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BASE_SCRIPT = (
    Path(__file__).resolve().parent.parent.parent
    / "json"
    / "jsonc-cst-util"
    / "scripts"
    / "jsonc_cst.py"
)


def read_jsonc(file_path: str) -> dict:
    """Read a JSONC file via the jsonc-cst-util base; return the parsed document.

    Raises FileNotFoundError when the base script is missing and ValueError when
    the input is not valid JSONC.
    """
    if not BASE_SCRIPT.is_file():
        raise FileNotFoundError(f"jsonc-cst-util base script not found: {BASE_SCRIPT}")
    proc = subprocess.run(
        [sys.executable, str(BASE_SCRIPT), "read", file_path],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip().removeprefix("ERROR: ") or f"exit code {proc.returncode}"
        raise ValueError(detail)
    return json.loads(proc.stdout)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file-path>", file=sys.stderr)
        return 1

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1

    try:
        data = read_jsonc(str(path))
    except Exception as error:
        print(f"ERROR: invalid JSONC: {error}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
