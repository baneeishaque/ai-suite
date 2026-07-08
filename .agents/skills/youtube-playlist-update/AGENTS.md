# YouTube Playlist Update — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md). Load that file for the full procedure, mandates, script reference, and verification steps.

## When This Skill Applies

- You need to rename a YouTube playlist (change its title).
- You need to update a playlist's description or privacy status.
- You are preparing a playlist for a new upload and its current name is outdated or incorrect.
- You are auditing or rebranding existing playlists across a channel.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`google-oauth-setup`](../google-oauth-setup/SKILL.md) — OAuth credential lifecycle (delegated by this skill)
- [`youtube-playlist-create`](../youtube-playlist-create/SKILL.md) — creating new playlists
- [`youtube-playlist-list`](../youtube-playlist-list/SKILL.md) — discovering playlist IDs
- [`youtube-playlist-item-add`](../youtube-playlist-item-add/SKILL.md) — adding videos to playlists
- [`youtube-video-snippet-update`](../youtube-video-snippet-update/SKILL.md) — base skill for updating video title/description/tags
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — composer that may trigger playlist rename
