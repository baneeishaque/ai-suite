# JSON Content Compare Ignore Keys — Companion Bridge

## Purpose

This file is the companion bridge for the
[`json-content-compare-ignore-keys`](SKILL.md) base primitive skill.
It exists so non-skill-aware agent runtimes (Codex CLI, some Cursor
profiles) discover this skill exists. The operational Single Source of
Truth lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Apply when any workflow needs to compare a JSON file against a baseline
while ignoring keys that are expected to change on every write
(auto-timestamps, nonces, runtime paths, machine IDs). The script
accepts `--file <path>` and repeatable `--ignore-keys <key>` arguments,
stores a SHA-256 snapshot of the filtered content, and exits 0 (MATCH)
or 1 (MISMATCH) on subsequent runs.

Do NOT apply when the comparison must be case-insensitive or
whitespace-tolerant — this primitive operates on parsed JSON only.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
environment requirements, script usage, exit codes, and first-run
snapshot seeding. Do NOT execute any step without first loading
`SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [Base Primitive — SKILL.md](SKILL.md) — the SSOT
- [`json-deep-sort`](../json-deep-sort/SKILL.md) — pre-normalization for inputs that need sorted arrays
- [`claude-config-change-gate`](../claude-config-change-gate/SKILL.md) — primary composer that consumes this primitive
