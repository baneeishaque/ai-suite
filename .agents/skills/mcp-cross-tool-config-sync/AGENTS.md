# AGENTS.md — mcp-cross-tool-config-sync

This file is a passive bridge. The active SSOT is [`SKILL.md`](SKILL.md).

## Purpose

Maintain a single canonical MCP server configuration and distribute schema-correct copies to every AI tool surface
(VS Code Copilot, JetBrains Copilot, Copilot CLI, Claude Desktop, Cursor, Windsurf, etc.) via a generator script
and symbolic links.

## When to read SKILL.md

Read [`SKILL.md`](SKILL.md) when the user asks to:

- Configure the same MCP server across multiple AI tools.
- Eliminate drift between per-tool MCP configs.
- Onboard a new AI tool to an existing MCP setup.
- Diagnose "tool X sees no MCP servers" while tool Y works.

## Deliverables

- A canonical `mcp-servers.json` (dominant `mcpServers` schema).
- A generator script ([`scripts/generate-configs.py`](scripts/generate-configs.py)) producing one file per tool.
- Symlinks from each tool's native config path → the corresponding generated file.
- Pre-symlink backups of every native file under `<canonical-root>/backups/`.

## Related

- [MCP Server Management Skill](../mcp-management/SKILL.md) — server-entry SSOT.
- [Tool Config Schema Probe Skill](../tool-config-schema-probe/SKILL.md) — base primitive used to discover
    schemas for new AI tools.
