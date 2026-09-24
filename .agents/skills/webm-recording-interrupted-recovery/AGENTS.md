# WebM Recording Interrupted Recovery — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You have two webm recording files from a meeting or screen recording that was interrupted — a main recording and a
continuation. The continuation may include content before the interruption point (recording restarted before the
presenter noticed). You want to trim the overlap, insert a "Recording interrupted" filler, and merge everything
into one seamless file — all without re-encoding the original video.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification
steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [FFmpeg Lossless Split](../ffmpeg-lossless-split/SKILL.md) — base skill invoked for trimming the continuation
- [WebM Recording Merge with Filler](../webm-recording-merge-with-filler/SKILL.md) — composer invoked for filler
  generation and merge
- [FFmpeg Lossless Concat](../ffmpeg-lossless-concat/SKILL.md) — base skill used transitively for lossless concat
- [System-Wide Tool Management](../system-wide-tool-management/SKILL.md) — installs ffmpeg/Pillow if missing
