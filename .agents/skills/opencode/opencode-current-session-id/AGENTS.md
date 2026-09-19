# OpenCode Current Session ID — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes that auto-load `AGENTS.md` by filename convention. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to programmatically discover the current opencode session ID and title from the logger logs in `.opencode/logs/`
- You are building a higher-level workflow that needs session-level traceability

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full composition rationale, CLI contract, protocol, and script reference. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`file-glob-sort-by-mtime`](../general/file/file-glob-sort-by-mtime/SKILL.md) — base primitive for finding the newest log file
- [`yaml-field-extract`](../general/yaml-field-extract/SKILL.md) — base primitive for extracting YAML header fields
