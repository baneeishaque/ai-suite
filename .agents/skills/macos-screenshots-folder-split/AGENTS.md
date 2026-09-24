# macOS Screenshots Folder Split — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Use this skill when you need to organize a flat folder of macOS screenshots
and screen recordings (files named `Screenshot YYYY-MM-DD at HH.MM.SS.png`
and `Screen Recording YYYY-MM-DD at HH.MM.SS.mov`) into YYYY-MM subfolders,
typically because OneDrive web cannot preview folders with more than ~5000
files. Metadata-only — no file content is ever read.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`onedrive-flat-folder-split-by-size`](../onedrive-flat-folder-split-by-size/SKILL.md) —
  upstream composer wrapped by this skill.
- [`file-glob-sort-by-regex-capture`](../file-glob-sort-by-regex-capture/SKILL.md) —
  upstream base for file listing and key extraction.
- [`json-group-stats`](../json-group-stats/SKILL.md) — upstream base for
  threshold checking.
- [`json-batch-file-move`](../json-batch-file-move/SKILL.md) — downstream
  base for batch file moves.
