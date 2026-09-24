# OpenCode Session YAML Tool-Call Extractor — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You have opencode logger-plugin YAML logs — a monolithic
  `ses_<id>.yaml` file OR a per-turn `ses_<id>/` directory of
  `NNN-*.yaml` files — and need every assistant tool call
  (`tool`, `args`, `result`) in chronological JSONL order
- You are auditing, analyzing, or recovering file changes from a
  session that has no `.md` session export (the YAML logs are the
  durable artifact)
- A higher-level extractor (`--yaml` mode) or the full-change audit
  composer delegates to this base skill

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure,
including the CLI contract, exit codes, and the YAML layout/schema
documentation. Do NOT execute any step without first loading
`SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`opencode-current-session-id`](../opencode-current-session-id/SKILL.md)
  — sibling in the `opencode/` group
