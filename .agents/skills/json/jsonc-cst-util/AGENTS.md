# jsonc-cst-util — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to read a JSONC file (JSON with `//` or `/* */` comments and/or
  trailing commas) and get strict JSON out without losing comments on write.
- You need to sort a JSON/JSONC file's object keys (and primitive arrays)
  while preserving every comment and the file's comma hygiene.
- You need to format a JSONC file with merge-friendly trailing commas so
  future edits never have to touch the previous item's line.
- You need mode-aware behavior: auto-detect JSONC vs strict JSON, force JSONC,
  or force strict with an explicit refusal when comments are present.

Do NOT apply when you only need to compare two JSON files — use the
`json-diff-leaf` primitive instead.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
mode-resolution table, CLI contract, comment model, sort/format semantics, and
verification steps. Do NOT execute any step without first loading `SKILL.md` —
this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`json-deep-sort`](../../json-deep-sort/SKILL.md) — composer that delegates
  sorting to this skill's `sort` subcommand.
- [`opencode-jsonc-util`](../../opencode-jsonc-util/SKILL.md) — wrapper that
  delegates JSONC reading to this skill's `read` subcommand.
- [`json-diff-leaf`](../../json-diff-leaf/SKILL.md) — related JSON comparison
  primitive.
