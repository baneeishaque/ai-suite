# File Glob Sort by mtime — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes that auto-load `AGENTS.md` by filename convention. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need the newest file(s) matching a glob pattern, sorted by modification time
- You need JSON Lines output with path, mtime, and size metadata
- You are composing a higher-level workflow that needs mtime-based file ordering

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full CLI contract, protocol, edge cases, and script reference. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`opencode-current-session-id`](../../opencode/opencode-current-session-id/SKILL.md) — composer that consumes this skill's output
