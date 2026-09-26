# OpenCode Installed-Plugin Lookup — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to know whether an opencode plugin is installed/enabled, where
  its plugin file lives, and where the logger writes its logs
- A higher-level skill must locate the logger layout before consuming
  `.opencode/logs/`

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the registry semantics and CLI contract.
Do NOT execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [`opencode-session-path-attribution`](../opencode-session-path-attribution/SKILL.md)
  — consumer: locates the logger via this skill before sweeping logs
- [`opencode-jsonc-util`](../../opencode-jsonc-util/SKILL.md) — consumed base
  for JSONC parsing (never re-rolled)
