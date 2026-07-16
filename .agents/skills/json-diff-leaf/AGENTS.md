# JSON Diff Leaf — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational Single Source of Truth lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to compare two JSON files and get a structured, machine-readable list of every leaf-value difference (added,
removed, changed, type-changed, reordered).
- You need a generic diff primitive to compose into a larger workflow (schema comparison, config drift detection, data
migration validation).
- You need deterministic JSON diff output for scripting or pipeline use.

Do NOT apply when you need human-readable formatted output with timestamp formatting, set-based list items, or summary
conclusions — use the [`json-diff-cli`](../json-diff-cli/SKILL.md) composer instead.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including CLI contract, change-kind reference table, and
verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-
actionable.

## Cross-References

- [`json-diff-cli`](../json-diff-cli/SKILL.md) — human-readable composer that calls this base skill via subprocess
- [`json-content-compare-ignore-keys`](../json-content-compare-ignore-keys/SKILL.md) — hash-based JSON comparison
(complementary)
- [`json-deep-sort`](../json-deep-sort/SKILL.md) — pre-normalization step before diffing
