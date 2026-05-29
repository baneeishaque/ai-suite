#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resolve the on-disk binary path for a tool installed via a non-default ``mise`` backend.

When a tool is installed via the default ``mise`` backend (the asdf-style
core plugin), ``mise which <tool>`` returns its absolute path. But when the
tool is sourced from a NON-default backend — ``github:org/repo``,
``ubi:org/repo``, ``asdf:org/repo``, ``http:...``, etc. — both
``mise which <tool>`` and ``mise where <tool>@latest`` fail with::

    mise ERROR <tool> is a mise bin however it is not currently active.
    mise ERROR <tool>@latest not installed

This script uses ``mise ls --json`` (whose top-level keys are the
backend-qualified specs like ``github:adwinying/php``) to locate the
matching install and emit ``<install_path>/<bin>`` on stdout.

Tier: 1 (Python 3.12+) per
``ai-agent-rules/scripting-language-selection-rules.md`` §2.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> str:
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(cmd)}\nstdout: {proc.stdout}\nstderr: {proc.stderr}"
        )
    return proc.stdout


def _short_name(spec: str) -> str:
    """``github:adwinying/php`` → ``php``; ``ubi:foo/bar`` → ``bar``; ``python`` → ``python``."""
    after_colon = spec.split(":", 1)[1] if ":" in spec else spec
    return after_colon.rsplit("/", 1)[-1]


def _backend_of(spec: str) -> str:
    return spec.split(":", 1)[0] if ":" in spec else ""


def _find_matches(
    ls: dict, tool: str, backend: str | None, version: str | None
) -> list[tuple[str, dict]]:
    matches: list[tuple[str, dict]] = []
    for spec, entries in ls.items():
        if _short_name(spec) != tool:
            continue
        if backend and _backend_of(spec) != backend:
            continue
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if version and entry.get("version") != version:
                continue
            matches.append((spec, entry))
    return matches


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mise_resolve_backend_bin.py",
        description="Resolve absolute binary path for a tool installed via a non-default mise backend.",
    )
    parser.add_argument("--tool", required=True, help="Short tool name (e.g., php)")
    parser.add_argument("--backend", default=None, help="Optional backend prefix filter (e.g., github)")
    parser.add_argument("--version", default=None, help="Optional version filter (e.g., 8.5.6)")
    parser.add_argument(
        "--bin",
        default=None,
        help="Optional binary name inside the install (defaults to --tool)",
    )
    parser.add_argument(
        "--require-installed",
        action="store_true",
        help="Reject entries whose `installed` field is false",
    )

    args = parser.parse_args(argv)

    try:
        raw = _run(["mise", "ls", "--json"])
        ls = json.loads(raw)
    except Exception as e:
        print(f"ERROR: `mise ls --json` failed: {e}", file=sys.stderr)
        return 2

    if not isinstance(ls, dict):
        print("ERROR: unexpected `mise ls --json` shape (not a dict)", file=sys.stderr)
        return 2

    matches = _find_matches(ls, args.tool, args.backend, args.version)
    if args.require_installed:
        matches = [(s, e) for s, e in matches if e.get("installed") is True]

    if not matches:
        print(
            f"ERROR: no mise install matches tool={args.tool!r} "
            f"backend={args.backend!r} version={args.version!r}",
            file=sys.stderr,
        )
        return 3
    if len(matches) > 1:
        descs = ", ".join(f"{s}@{e.get('version', '?')}" for s, e in matches)
        print(
            f"ERROR: multiple mise installs match tool={args.tool!r}; "
            f"disambiguate with --backend / --version: {descs}",
            file=sys.stderr,
        )
        return 4

    spec, entry = matches[0]
    install_path = entry.get("install_path")
    if not install_path:
        print(f"ERROR: entry {spec!r} has no install_path", file=sys.stderr)
        return 5

    bin_name = args.bin or args.tool
    bin_path = Path(install_path) / bin_name
    if not bin_path.exists():
        alt = Path(install_path) / "bin" / bin_name
        if alt.exists():
            bin_path = alt
        else:
            print(
                f"ERROR: binary {bin_name!r} not found under {install_path!r}",
                file=sys.stderr,
            )
            return 6

    print(bin_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
