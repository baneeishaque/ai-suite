#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Idempotently write a VS Code setting into one or more scope files.

A scope file is either:

* a folder-mode settings file (``<repo>/.vscode/settings.json``) — top-level
  keys are setting names, OR
* a workspace-mode workspace file (``*.code-workspace``) — settings live
  under the top-level ``"settings"`` object.

The script auto-detects which form each ``--scope`` path is, by file
extension and presence of the top-level ``settings`` key.

Tier: 1 (Python 3.12+) — chosen per
``ai-agent-rules/scripting-language-selection-rules.md`` §2 (file-mutation +
JSON + cross-OS). The Tier-2 PowerShell craftsmanship rules in
``skill-factory/SKILL.md`` §2.2.1 items 2–8 DO NOT apply to this script.

Usage (single setting, two scopes)::

    python3 write_vscode_setting.py \\
        --key php.validate.executablePath \\
        --value /Users/me/.local/share/mise/installs/.../php \\
        --value-type string \\
        --scope /path/to/repo/.vscode/settings.json \\
        --scope /path/to/workspace.code-workspace

Exit codes
----------
* ``0`` — every scope written (or already correct; idempotent).
* ``1`` — usage error.
* ``2`` — any scope file unreadable / unparseable / unwritable.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _detect_scope_kind(path: Path) -> str:
    """Return ``"workspace"`` for ``*.code-workspace`` files, else ``"folder"``."""
    return "workspace" if path.suffix == ".code-workspace" else "folder"


def _coerce_value(raw: str, value_type: str) -> Any:
    if value_type == "string":
        return raw
    if value_type == "bool":
        low = raw.strip().lower()
        if low in ("true", "1", "yes", "on"):
            return True
        if low in ("false", "0", "no", "off"):
            return False
        raise ValueError(f"--value {raw!r} is not a boolean")
    if value_type == "int":
        return int(raw)
    if value_type == "float":
        return float(raw)
    if value_type == "json":
        return json.loads(raw)
    raise ValueError(f"Unknown --value-type {value_type!r}")


def _strip_jsonc(text: str) -> str:
    """State-aware stripper for `//` line comments, `/* */` block comments, and trailing commas.

    Respects double-quoted strings (with backslash escapes) so URLs inside
    string values are not mangled.
    """
    out: list[str] = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    stripped = "".join(out)
    import re

    return re.sub(r",(\s*[}\]])", r"\1", stripped)


def _load_jsonc(path: Path) -> dict:
    """Tolerantly load a JSONC-ish file (VS Code allows ``//``, ``/* */``, trailing commas)."""
    text = path.read_text(encoding="utf-8")
    return json.loads(_strip_jsonc(text))


def _write_json(path: Path, data: dict, indent: int = 4) -> None:
    serialized = json.dumps(data, indent=indent, ensure_ascii=False) + "\n"
    path.write_bytes(serialized.encode("utf-8"))


def _set_at(container: dict, key: str, value: Any) -> bool:
    """Set ``key`` to ``value`` in ``container``; return True if changed."""
    if key in container and container[key] == value:
        return False
    container[key] = value
    return True


def _apply_to_scope(path: Path, key: str, value: Any) -> tuple[str, bool]:
    if not path.exists():
        if path.suffix == ".code-workspace":
            print(f"ERROR: workspace file does not exist: {path}", file=sys.stderr)
            return ("error", False)
        path.parent.mkdir(parents=True, exist_ok=True)
        data: dict = {}
    else:
        try:
            data = _load_jsonc(path)
        except (OSError, ValueError) as e:
            print(f"ERROR: cannot parse {path}: {e}", file=sys.stderr)
            return ("error", False)

    kind = _detect_scope_kind(path)
    if kind == "workspace":
        if not isinstance(data.get("settings"), dict):
            data["settings"] = {}
        changed = _set_at(data["settings"], key, value)
    else:
        changed = _set_at(data, key, value)

    if changed:
        try:
            _write_json(path, data)
        except OSError as e:
            print(f"ERROR: cannot write {path}: {e}", file=sys.stderr)
            return ("error", False)
    return (kind, changed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="write_vscode_setting.py",
        description="Idempotently write a VS Code setting into one or more scope files.",
    )
    parser.add_argument("--key", required=True, help="Setting key, e.g., php.validate.executablePath")
    parser.add_argument("--value", required=True, help="Setting value (raw string; see --value-type)")
    parser.add_argument(
        "--value-type",
        choices=("string", "bool", "int", "float", "json"),
        default="string",
        help="How to coerce --value (default: string)",
    )
    parser.add_argument(
        "--scope",
        action="append",
        required=True,
        type=Path,
        help="Absolute path to a .vscode/settings.json OR a .code-workspace; repeat for multiple",
    )

    args = parser.parse_args(argv)

    try:
        value = _coerce_value(args.value, args.value_type)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    exit_code = 0
    for scope_path in args.scope:
        scope_path = scope_path.resolve()
        kind, changed = _apply_to_scope(scope_path, args.key, value)
        if kind == "error":
            exit_code = 2
            continue
        verb = "UPDATED" if changed else "ALREADY-SET"
        print(f"{verb} [{kind}] {scope_path} :: {args.key}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
