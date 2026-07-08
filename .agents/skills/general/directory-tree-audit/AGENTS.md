# Directory Tree Audit — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT resides in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to audit a directory tree to understand how many items each folder
  contains.
- You need to identify folders that exceed a configurable item-count threshold
  (overstuffed folders that may need sub-grouping).
- You are building or invoking a higher-level composer that consumes structured
  directory data (e.g., the 8±2 human-scanability principle).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
script reference, protocol, and output contract. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with script reference, protocol, and output
  contract.
- [`human-scanable-organization`](../human-scanable-organization/SKILL.md) —
  composer skill that consumes this skill's output.
