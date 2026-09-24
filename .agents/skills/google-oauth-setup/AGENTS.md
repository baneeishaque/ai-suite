# Google OAuth Setup — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to authenticate against any Google API (YouTube, Calendar, Sheets, Drive, Gmail) via OAuth2. This skill handles the full credential lifecycle: detect expired tokens, refresh them automatically, or initiate a browser-based PKCE flow when no refresh token exists.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including scripts, verification steps, and edge-case handling. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`youtube-playlist-list`](../youtube-playlist-list/SKILL.md) — composer that uses this base for API auth
- [`youtube-video-snippet-update`](../youtube-video-snippet-update/SKILL.md) — base skill that uses this skill for Data API auth (video snippet update)
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — composer that uses this base for upload auth
- [`youtube-video-metadata-update`](../youtube-video-metadata-update/SKILL.md) — base skill that uses this skill for Data API auth
