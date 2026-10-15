# json-deep-sort — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to sort a JSON or JSONC file's object keys alphabetically (and
  primitive arrays) for diff stability or readability.
- The file may contain comments and trailing commas that must survive the
  sort.
- You want a one-command, in-place deep-sort over one or more files.

Do NOT apply when you need a structural comparison of two JSON files — use
the `json-diff-leaf` primitive instead.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
CLI contract, sort semantics, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`jsonc-cst-util`](../json/jsonc-cst-util/SKILL.md) — base primitive that
  performs the CST parse, sort, and merge-friendly serialization.
- [`json-diff-leaf`](../json-diff-leaf/SKILL.md) — related JSON comparison
  primitive.
