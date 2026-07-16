# FFmpeg Lossless Split — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You have a media file that needs to be split into two parts at a specific timestamp, or you need to extract a segment
between two timestamps — without re-encoding (zero quality loss). The skill validates the timestamps against the file
duration before executing.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification
steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [FFmpeg Lossless Concat](../ffmpeg-lossless-concat/SKILL.md) — sibling base skill for lossless concatenation
- [WebM Recording Merge with Filler](../webm-recording-merge-with-filler/SKILL.md) — composer that merges webm
  segments with filler transitions
- [WebM Recording Interrupted Recovery](../webm-recording-interrupted-recovery/SKILL.md) — composer that invokes
  this skill to trim continuation recordings before merging
- [System-Wide Tool Management](../system-wide-tool-management/SKILL.md) — installs ffmpeg/ffprobe if missing
