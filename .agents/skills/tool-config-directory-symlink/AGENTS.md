# Tool Config Directory Symlink — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

When migrating any tool's configuration directories (config, state, data, cache)
from their native XDG locations into a managed companion repo
(`<private-repo>` or similar), replacing the originals with symlinks.
The skill is domain-agnostic — it does not define which files to track; that is
delegated to tool-specific composers.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all
mandates, scripts, and verification steps. Do NOT execute any step without
first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`opencode-config-preserve`](../opencode-config-preserve/SKILL.md) — Composer for OpenCode-specific config preservation
- [`dev-env-private-config-symlink`](../dev-env-private-config-symlink/SKILL.md)
  — Related symlink protocol for app-level configs
- [`mcp-cross-tool-config-sync`](../mcp-cross-tool-config-sync/SKILL.md) — Related config-symlink lifecycle for MCP servers
