#!/usr/bin/env python3
"""Generate per-tool MCP configuration files from a single canonical SSOT.

Canonical schema (./mcp-servers.json relative to this script's parent.parent):
    {
      "inputs":     [...],          # optional, VS Code-only field, passed through
      "mcpServers": { name: {...} } # required, dominant MCP schema
    }

Generated per-tool outputs are written to ./generated/<tool>/<filename>.
Each tool then symlinks its native config file to the generated counterpart.

Usage:
    python3 scripts/generate-configs.py

Adding a new tool:
    1. Write a gen_<tool>(canonical) function below.
    2. Append it to the GENERATORS tuple.
    3. Symlink the tool's native config path to ./generated/<tool>/<filename>.

This is a reusable template. The active copy for a given user lives next to
their canonical mcp-servers.json (typically a private configuration tree).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "mcp-servers.json"
OUT = ROOT / "generated"


def load_canonical() -> dict:
    if not CANONICAL.exists():
        sys.exit(f"canonical file missing: {CANONICAL}")
    with CANONICAL.open() as fh:
        data = json.load(fh)
    if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
        sys.exit("canonical must contain an object 'mcpServers'")
    return data


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    print(f"  wrote {path.relative_to(ROOT)}")


def with_stdio_default(server: dict) -> dict:
    """Inject 'type': 'stdio' if the entry has a 'command' field but no 'type'."""
    out = dict(server)
    if "command" in out and "type" not in out:
        out = {"type": "stdio", **out}
    return out


# ---------- per-tool generators ----------


def gen_copilot_cli(canonical: dict) -> None:
    """GitHub Copilot CLI - same 'mcpServers' key, adds 'tools': ['*'] per server."""
    servers = {}
    for name, srv in canonical["mcpServers"].items():
        srv = with_stdio_default(srv)
        if "tools" not in srv:
            srv = {**srv, "tools": ["*"]}
        servers[name] = srv
    write_json(OUT / "copilot-cli" / "mcp-config.json", {"mcpServers": servers})


def gen_vscode(canonical: dict) -> None:
    """VS Code GitHub Copilot - 'servers' key (+ pass-through 'inputs')."""
    payload: dict = {}
    if "inputs" in canonical:
        payload["inputs"] = canonical["inputs"]
    payload["servers"] = {
        name: with_stdio_default(srv)
        for name, srv in canonical["mcpServers"].items()
    }
    write_json(OUT / "vscode" / "mcp.json", payload)


def gen_jetbrains(canonical: dict) -> None:
    """JetBrains GitHub Copilot - 'servers' key, no 'inputs'."""
    servers = {
        name: with_stdio_default(srv)
        for name, srv in canonical["mcpServers"].items()
    }
    write_json(OUT / "jetbrains" / "mcp.json", {"servers": servers})


GENERATORS = (gen_copilot_cli, gen_vscode, gen_jetbrains)


def main() -> int:
    canonical = load_canonical()
    print(f"canonical: {CANONICAL.relative_to(ROOT)}")
    print(f"output:    {OUT.relative_to(ROOT)}/")
    for gen in GENERATORS:
        gen(canonical)
    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
