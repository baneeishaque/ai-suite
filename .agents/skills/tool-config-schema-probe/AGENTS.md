# AGENTS.md — tool-config-schema-probe

Passive bridge. Active SSOT is [`SKILL.md`](SKILL.md).

## Purpose

Reverse-engineer the on-disk config file path and JSON/TOML/YAML schema of any tool whose configuration format
is undocumented, by writing a sentinel "dummy" entry through the tool's own UI and diffing the filesystem.

## When to read SKILL.md

- A tool's MCP / plugin / extension config path is unknown or differs from docs.
- The schema's top-level key or per-entry shape is unclear.
- A vendor's CLI vs. IDE-plugin config relationship is ambiguous.

## Output

A documented record: tool + version + OS + canonical path + top-level key + per-entry fields + reload behavior.
Consumers cache this record so the probe is a one-time cost per tool/version pair.

## Known consumers

- [MCP Cross-Tool Config Sync](../mcp-cross-tool-config-sync/SKILL.md)
