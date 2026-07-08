# FFmpeg Lossless Concat — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You have two or more media files (webm, mp4, mkv, etc.) with identical codec parameters and need to join them into a
single file without re-encoding (zero quality loss). The skill verifies codec compatibility first, then runs ffmpeg's
concat demuxer with `-c copy`.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification
steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [WebM Recording Merge with Filler](../webm-recording-merge-with-filler/SKILL.md) — composer that feeds into this base
- [System-Wide Tool Management](../system-wide-tool-management/SKILL.md) — installs ffmpeg/ffprobe if missing
