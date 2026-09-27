# JSON Diff CLI — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational Single Source of Truth lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to compare two JSON files and get a clean human-readable report of every difference, with timestamp dates,
set-based list diffs, and a conclusion.
- You want to know which file is newer, which items were added/removed from arrays, and whether one file is a superset
of the other.
- You are an end user (not a pipeline) who wants to visually inspect the diff of two JSON config files.

Do NOT apply when you need a machine-readable change list for scripting — use the [`json-diff-leaf`](../json-diff-
leaf/SKILL.md) base primitive directly.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including CLI usage, output format reference, and
verification examples. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-
actionable.

## Cross-References

- [`json-diff-leaf`](../json-diff-leaf/SKILL.md) — base primitive that this composer calls via subprocess
- [`json-content-compare-ignore-keys`](../json-content-compare-ignore-keys/SKILL.md) — hash-based JSON comparison
(complementary)
- [`json-deep-sort`](../json-deep-sort/SKILL.md) — pre-normalization step before diffing
- [`folder-comparison`](../folder-comparison/SKILL.md) — directory-level comparison
