# Media Timestamp Summary — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Use this skill when you have a directory of media files whose filenames
contain Unix epoch-millisecond timestamps (e.g. `video-1780724440748.webm`),
and you want to generate a human-readable summary ordered chronologically
with file sizes, readable dates, and time gaps between recordings.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`file-glob-sort-by-regex-capture`](../file-glob-sort-by-regex-capture/SKILL.md)
  — base skill composed by this skill for deterministic file sorting.
- [`webm-recording-merge-with-filler`](../webm-recording-merge-with-filler/SKILL.md)
  — sibling media-processing composer for merging discontinuous recordings.
- [`webm-recording-interrupted-recovery`](../webm-recording-interrupted-recovery/SKILL.md)
  — sibling composer for recording interruption recovery.
