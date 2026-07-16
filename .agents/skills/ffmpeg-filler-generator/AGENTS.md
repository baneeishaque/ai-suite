# FFmpeg Filler Generator — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to generate a short filler or transition video segment — black background with centered custom text,
silent audio, any duration — for insertion between other video segments. Common scenarios include:

- "Recording interrupted" cards between meeting recording segments
- "Content missing" placeholders in podcast or screen-capture edits
- Chapter divider cards in video assemblies

The skill outputs a single video file; it does NOT concatenate or merge.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification
steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [FFmpeg Lossless Concat](../ffmpeg-lossless-concat/SKILL.md) — sibling base skill for lossless concatenation
- [WebM Recording Merge with Filler](../webm-recording-merge-with-filler/SKILL.md) — composer that invokes this base skill
- [System-Wide Tool Management](../system-wide-tool-management/SKILL.md) — installs ffmpeg / Pillow if missing
