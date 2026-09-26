#!/usr/bin/env python3
"""Generate per-tool MCP configuration files from a single canonical SSOT,
and (by default) deploy a relative symlink at each consumer's expected path.

Canonical schema (./mcp-servers.json relative to this script's parent.parent):
    {
      "inputs":     [...],          # optional, VS Code-only field, passed through
      "mcpServers": { name: {...} } # required, dominant MCP schema
    }

Generated per-tool outputs are written to ./generated/<tool>/<filename>.

Each tool's consumer-side symlink (e.g., User/mcp.json -> ../../mcp/generated/vscode/mcp.json)
is deployed automatically as a RELATIVE symlink, idempotently, ONLY when the
parent directory of the link exists on this machine. Pass --no-deploy to skip.

Adding a new tool:
    1. Write a gen_<tool>(canonical) function below.
    2. Append it to the GENERATORS tuple.
    3. (Optional) Register a deploy target in DEPLOY_TARGETS so the consumer
       symlink is created automatically. Keep the link path RELATIVE to ROOT
       — the script computes the relative-symlink target itself.

This is a reusable template. The active copy for a given user lives next to
their canonical mcp-servers.json (typically a private configuration tree).

Usage:
    python3 scripts/generate-configs.py            # generate + deploy symlinks
    python3 scripts/generate-configs.py --no-deploy # generate only
"""

from __future__ import annotations

import argparse
import json
import os
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


def deploy_symlink(link: Path, target: Path) -> None:
    """Create a RELATIVE symlink at `link` pointing to `target`, idempotently.

    Skips silently (with a notice) if the link's PARENT directory does not exist
    on this machine — that consumer is not installed here.
    Replaces any existing file/symlink at `link`. Errors loudly on directories.
    """
    if not link.parent.exists():
        print(f"  skip-link  {link}  (parent dir absent on this machine)")
        return
    if not target.exists():
        print(f"  skip-link  {link}  (target {target} missing)", file=sys.stderr)
        return
    if link.is_symlink() or link.exists():
        if link.is_dir() and not link.is_symlink():
            sys.exit(f"refusing to replace directory at link path: {link}")
        link.unlink()
    relative = os.path.relpath(target, link.parent)
    link.symlink_to(relative)
    print(f"  linked    {link}  ->  {relative}")


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


def gen_claude_desktop(canonical: dict) -> None:
    """Claude Desktop - passthrough 'mcpServers' key unchanged."""
    write_json(OUT / "claude-desktop" / "claude_desktop_config.json",
               {"mcpServers": canonical["mcpServers"]})


def gen_cursor(canonical: dict) -> None:
    """Cursor - passthrough 'mcpServers' key unchanged."""
    write_json(OUT / "cursor" / "mcp.json",
               {"mcpServers": canonical["mcpServers"]})


def gen_windsurf(canonical: dict) -> None:
    """Windsurf - passthrough 'mcpServers' key unchanged."""
    write_json(OUT / "windsurf" / "mcp_config.json",
               {"mcpServers": canonical["mcpServers"]})


def gen_opencode(canonical: dict) -> None:
    """OpenCode - rename 'mcpServers' key to 'mcp', drop 'inputs'.

    Remote servers (those with 'type': 'remote') keep their 'url' + 'headers';
    stdio servers get 'type': 'stdio' default injected via with_stdio_default.
    """
    servers = {
        name: with_stdio_default(srv)
        for name, srv in canonical["mcpServers"].items()
    }
    write_json(OUT / "opencode" / "opencode.json", {"mcp": servers})


GENERATORS = (gen_copilot_cli, gen_vscode, gen_jetbrains,
              gen_claude_desktop, gen_cursor, gen_windsurf, gen_opencode)

# Consumer-side symlink deployment map.
# Key   = tool id (matches a gen_<tool> function's domain).
# Value = (link path relative to ROOT, target path relative to ROOT).
# Only entries whose link.parent EXISTS on the current machine are deployed
# (allows the same canonical script to run on machines without every consumer
# tool installed). Add new tools' deploy targets here as paths become known.
DEPLOY_TARGETS: dict[str, tuple[str, str]] = {
    "vscode": (
        # ROOT here is <canonical-root>/mcp. For the typical private-config layout
        # where the User folder is a sibling of mcp/, this resolves to
        # ../vscode-insiders-configuration/visual-studio-code-user-settings/mcp.json
        "../vscode-insiders-configuration/visual-studio-code-user-settings/mcp.json",
        "generated/vscode/mcp.json",
    ),
    "claude-desktop": (
        "../claude/claude_desktop_config.json",
        "generated/claude-desktop/claude_desktop_config.json",
    ),
    "cursor": (
        "../.cursor/mcp.json",
        "generated/cursor/mcp.json",
    ),
    "windsurf": (
        "../.codeium/windsurf/mcp_config.json",
        "generated/windsurf/mcp_config.json",
    ),
    "opencode": (
        "../.config/opencode/opencode.json",
        "generated/opencode/opencode.json",
    ),
}


def deploy_all() -> None:
    for tool, (link_rel, target_rel) in DEPLOY_TARGETS.items():
        deploy_symlink(ROOT / link_rel, ROOT / target_rel)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-deploy", action="store_true",
                        help="generate per-tool config files but do NOT deploy consumer symlinks")
    args = parser.parse_args()

    canonical = load_canonical()
    print(f"canonical: {CANONICAL.relative_to(ROOT)}")
    print(f"output:    {OUT.relative_to(ROOT)}/")
    for gen in GENERATORS:
        gen(canonical)
    if args.no_deploy:
        print("done (no consumer symlinks deployed).")
    else:
        print("deploying consumer symlinks:")
        deploy_all()
        print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
