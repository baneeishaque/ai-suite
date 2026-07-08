# URL Shortcut Creator — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to create a clickable `.html` file that opens a specific URL in the
browser — for example, after uploading a video to YouTube, create a shortcut so
the user can double-click to view it instead of memorising the URL.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
script invocation with all flag options. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — composer that uses this skill to create post-upload URL shortcuts
