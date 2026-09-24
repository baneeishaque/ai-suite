# JSON Batch File Move — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Use this skill when you need to move files into subfolders based on a JSON
manifest that pairs each file's absolute path (`abspath`) with a destination
folder name (`key`). The skill is domain-agnostic — it works for any batch
move operation: organizing downloads by filetype, distributing assets by
deployment bucket, archiving logs by date. Metadata-only — no file content
is ever read.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`json-group-stats`](../json-group-stats/SKILL.md) — upstream pre-check
  for group-size validation before invoking this skill.
- [`onedrive-flat-folder-split-by-size`](../onedrive-flat-folder-split-by-size/SKILL.md) —
  composer that orchestrates the full pipeline including this skill.
- [`file-glob-sort-by-regex-capture`](../file-glob-sort-by-regex-capture/SKILL.md) —
  upstream producer of the JSON manifest consumed by this skill.
