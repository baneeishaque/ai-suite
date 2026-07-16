# WebM Recording Merge with Filler — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You have two or more discontinuous webm recording segments from a meeting, call, or screen recording that need to be
merged into one file. In between the segments, a filler transition (black screen with custom text) should be inserted
to indicate where content is missing — without re-encoding the original segments (zero quality loss).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification
steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [FFmpeg Filler Generator](../ffmpeg-filler-generator/SKILL.md) — base skill invoked for generating the filler transition
- [FFmpeg Lossless Concat](../ffmpeg-lossless-concat/SKILL.md) — base skill invoked for lossless concatenation
- [System-Wide Tool Management](../system-wide-tool-management/SKILL.md) — installs ffmpeg / Pillow if missing
