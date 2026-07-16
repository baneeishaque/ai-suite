# Media Audio Language Detect — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to determine the spoken language of a video or audio file — for example, to populate the `--language` flag before uploading to YouTube, or to classify media files by language.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the language detection script with all flag options and output formats. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — composer that uses this skill for pre-upload language detection
- [`youtube-video-metadata-update`](../youtube-video-metadata-update/SKILL.md) — consumer of the detected language code
