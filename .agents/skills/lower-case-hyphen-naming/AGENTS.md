# Lower Case Hyphen Naming — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to enforce lowercase kebab-case naming for files, directories, or identifiers — or you detect files/directories with spaces, underscores, or mixed casing. Also applies when renaming files before upload workflows (e.g., YouTube upload) for consistent naming.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the blast-radius trace, rename execution, and cross-reference update steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`lower-case-underscore-naming`](../lower-case-underscore-naming/SKILL.md) — sibling skill for snake_case convention
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — optional consumer that may invoke kebab-case rename before upload
