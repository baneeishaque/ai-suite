# OneDrive Flat Folder Split by Size — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Use this skill when you need to organize a flat OneDrive folder whose file
count exceeds the ~5000-file web preview limit. The skill splits files into
key-named subfolders (e.g. `2025-11/`, `2025-12/`) based on a regex capture
group extracted from each filename. Metadata-only — no file content is ever
read, avoiding OneDrive download triggers.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`macos-screenshots-folder-split`](../macos-screenshots-folder-split/SKILL.md) —
  domain composer that wraps this skill with macOS screenshot defaults.
- [`file-glob-sort-by-regex-capture`](../file-glob-sort-by-regex-capture/SKILL.md) —
  upstream base for file listing and key extraction.
- [`json-group-stats`](../json-group-stats/SKILL.md) — upstream base for
  per-group threshold checking.
- [`json-batch-file-move`](../json-batch-file-move/SKILL.md) — downstream
  base for batch file moves.
