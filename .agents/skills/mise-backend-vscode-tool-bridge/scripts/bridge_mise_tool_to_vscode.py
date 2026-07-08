#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Composer — wire a mise-installed binary into VS Code interpreter settings across multiple scopes.

End-to-end orchestration:

1. Resolve the binary path via the
   ``mise-non-standard-backend-bin-resolve`` base skill.
2. For every consumer setting key (built-in for the chosen language), write
   the resolved path into every requested scope via the
   ``vscode-multi-scope-setting-write`` base skill.

Each base script is invoked through ``subprocess.run`` using a path
resolved relative to THIS script's own location (per
``ai-rule-standardization-rules`` §Portable Script Path Mandate), so the
composer works regardless of the caller's cwd.

Tier: 1 (Python 3.12+) per
``ai-agent-rules/scripting-language-selection-rules.md`` §2.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
RESOLVE_SCRIPT = (
    SCRIPT_DIR
    / ".."
    / ".."
    / "mise-non-standard-backend-bin-resolve"
    / "scripts"
    / "mise_resolve_backend_bin.py"
).resolve()
WRITE_SCRIPT = (
    SCRIPT_DIR
    / ".."
    / ".."
    / "vscode-multi-scope-setting-write"
    / "scripts"
    / "write_vscode_setting.py"
).resolve()


LANGUAGE_BUILTIN_KEYS: dict[str, list[str]] = {
    "php": [
        "php.validate.executablePath",
        "php.debug.executablePath",
    ],
    # Extension surface — add new languages here as they are validated:
    # "python": ["python.defaultInterpreterPath"],
    # "go":     ["go.alternateTools.go"],
}


def _run_capture(cmd: list[str]) -> str:
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed (exit {proc.returncode}): {' '.join(cmd)}\n"
            f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
        )
    return proc.stdout.strip()


def _run_passthrough(cmd: list[str]) -> int:
    return subprocess.run(cmd, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bridge_mise_tool_to_vscode.py",
        description=(
            "Resolve a mise-installed binary and write its path into the "
            "built-in VS Code interpreter settings for the language, across "
            "one or more scope files (folder settings.json and/or "
            ".code-workspace)."
        ),
    )
    parser.add_argument(
        "--language",
        required=True,
        choices=sorted(LANGUAGE_BUILTIN_KEYS),
        help="Target language whose built-in interpreter settings to write",
    )
    parser.add_argument("--tool", default=None, help="mise short tool name (defaults to --language)")
    parser.add_argument("--backend", default=None, help="Optional mise backend filter (e.g., github)")
    parser.add_argument("--version", default=None, help="Optional version filter")
    parser.add_argument(
        "--bin",
        default=None,
        help="Optional binary name inside the install (defaults to --tool / --language)",
    )
    parser.add_argument(
        "--scope",
        action="append",
        required=True,
        type=Path,
        help="Absolute path to a .vscode/settings.json OR a .code-workspace; repeat for multiple",
    )
    parser.add_argument(
        "--extra-key",
        action="append",
        default=[],
        help="Extra setting key to write the binary path into (repeatable)",
    )

    args = parser.parse_args(argv)

    for script_path, label in [
        (RESOLVE_SCRIPT, "mise-non-standard-backend-bin-resolve"),
        (WRITE_SCRIPT, "vscode-multi-scope-setting-write"),
    ]:
        if not script_path.exists():
            print(
                f"ERROR: base-skill script missing — expected {label} at {script_path}",
                file=sys.stderr,
            )
            return 10

    tool = args.tool or args.language
    bin_name = args.bin or tool

    resolve_cmd = [
        sys.executable,
        str(RESOLVE_SCRIPT),
        "--tool",
        tool,
        "--bin",
        bin_name,
    ]
    if args.backend:
        resolve_cmd += ["--backend", args.backend]
    if args.version:
        resolve_cmd += ["--version", args.version]

    try:
        bin_path = _run_capture(resolve_cmd)
    except RuntimeError as e:
        print(f"ERROR: resolve step failed: {e}", file=sys.stderr)
        return 11

    if not bin_path:
        print("ERROR: resolver returned empty path", file=sys.stderr)
        return 12

    keys = list(LANGUAGE_BUILTIN_KEYS[args.language]) + list(args.extra_key)
    print(f"RESOLVED {args.language} → {bin_path}")
    print(f"WRITING  {len(keys)} key(s) × {len(args.scope)} scope(s)")

    overall_rc = 0
    for key in keys:
        write_cmd = [
            sys.executable,
            str(WRITE_SCRIPT),
            "--key",
            key,
            "--value",
            bin_path,
            "--value-type",
            "string",
        ]
        for scope in args.scope:
            write_cmd += ["--scope", str(scope)]
        rc = _run_passthrough(write_cmd)
        if rc != 0:
            print(f"ERROR: write step failed for key {key!r} (exit {rc})", file=sys.stderr)
            overall_rc = 13

    return overall_rc


if __name__ == "__main__":
    sys.exit(main())
