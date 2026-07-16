# File Glob Sort by Regex Capture — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Use this skill when you need to list files in a directory, sort them by a
value extracted from their filename (timestamp, sequence number, date string,
etc.), and output the sorted list as machine-readable JSON Lines. The skill
is domain-agnostic — it works for any filename pattern that embeds a sortable
key in a regex-capturable position.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`media-timestamp-summary`](../media-timestamp-summary/SKILL.md) — composer
  that consumes this base skill for media-file chronological sorting.
- [`text-lines-sort-by-length`](../text-lines-sort-by-length/SKILL.md) —
  sibling base primitive for sorting text file lines by length.
