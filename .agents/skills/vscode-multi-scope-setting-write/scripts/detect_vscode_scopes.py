#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enumerate VS Code setting scopes relevant to a target folder.

Given a folder path (a repository or project root), emit on stdout one
absolute path per line for each scope file the operator should consider
when writing settings:

* ``<folder>/.vscode/settings.json`` (folder-mode), unconditionally.
* Any ``.code-workspace`` files passed explicitly via ``--workspace`` (these
  are not auto-discoverable on disk in the general case because users keep
  them anywhere, e.g., inside a ``configurations-private`` repo).

When a ``.code-workspace`` is supplied, it is listed FIRST because workspace
settings override folder settings — so callers writing to both scopes can
iterate in deterministic precedence order.

Tier: 1 (Python 3.12+).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="detect_vscode_scopes.py",
        description="Print VS Code scope paths for a folder, workspace-first.",
    )
    parser.add_argument("--folder", required=True, type=Path, help="Repository / project root")
    parser.add_argument(
        "--workspace",
        action="append",
        type=Path,
        default=[],
        help="Absolute path to a .code-workspace file currently in use (repeat for multiple)",
    )
    args = parser.parse_args(argv)

    folder = args.folder.resolve()
    if not folder.is_dir():
        print(f"ERROR: --folder is not a directory: {folder}", file=sys.stderr)
        return 1

    for ws in args.workspace:
        ws_abs = ws.resolve()
        if ws_abs.suffix != ".code-workspace":
            print(f"WARNING: --workspace path is not .code-workspace: {ws_abs}", file=sys.stderr)
        print(ws_abs)

    print(folder / ".vscode" / "settings.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
