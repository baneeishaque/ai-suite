# SSOT Provider Extension Sync — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

When you need to extend base OpenCode provider definitions (from models.json) into multiple per-account provider entries with API keys from a key-value file, syncing across opencode.json, auth.json, and account.json.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the tracking file format, naming convention, and script invocation. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`kv-line-parse`](../../general/kv-line-parse/SKILL.md) — Base skill for key-value line parsing, consumed by this composer for key lookups.
- [`opencode-config-preserve`](../../opencode-config-preserve/SKILL.md) — Companion skill for OpenCode XDG config preservation.
- [`opencode-provider-persistence-config`](../../opencode-provider-persistence-config/SKILL.md) — Base skill for auth.json persistence model.
