# YAML Field Extract — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes that auto-load `AGENTS.md` by filename convention. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to extract a single value from a YAML file by dot-separated key path
- You are working with multi-document YAML and need to select a specific document
- You are composing a higher-level workflow that needs YAML field extraction (e.g., parsing opencode session headers)

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full CLI contract, protocol, edge cases, and script reference. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`opencode-current-session-id`](../../opencode/opencode-current-session-id/SKILL.md) — composer that consumes this skill's output
