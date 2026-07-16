# JSON Group Stats — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Use this skill when you need to group JSON records by a field value and
obtain per-group counts or the grouped records themselves. The skill is
domain-agnostic — it works for any JSON array of flat dicts: log entries
by severity, test results by suite, file metadata by date key, API
responses by status code.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`json-batch-file-move`](../json-batch-file-move/SKILL.md) — downstream
  consumer for grouped file-move operations.
- [`onedrive-flat-folder-split-by-size`](../onedrive-flat-folder-split-by-size/SKILL.md) —
  composer that uses this skill for OneDrive threshold checking.
- [`file-glob-sort-by-regex-capture`](../file-glob-sort-by-regex-capture/SKILL.md) —
  upstream producer whose JSON Lines output feeds into this skill.
