# YouTube Playlist List — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to see the authenticated user's YouTube playlists — for example, to choose a target playlist before uploading a video, to audit existing playlists, or to plan content migration.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including credential management via [`google-oauth-setup`](../google-oauth-setup/SKILL.md) and the playlist listing script. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`google-oauth-setup`](../google-oauth-setup/SKILL.md) — base skill for OAuth credential lifecycle
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — composer that uses this skill for playlist selection
