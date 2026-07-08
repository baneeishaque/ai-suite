# YouTube Playlist Item Add — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to add an existing YouTube video to a playlist — for example, after uploading a video to add it to a second playlist (dual-playlist membership), when organizing existing channel videos into topic playlists, or when migrating content between playlists.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including credential management via [`google-oauth-setup`](../google-oauth-setup/SKILL.md) and the playlist item add script. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`google-oauth-setup`](../google-oauth-setup/SKILL.md) — base skill for OAuth credential lifecycle
- [`youtube-playlist-list`](../youtube-playlist-list/SKILL.md) — base skill for listing existing playlists
- [`youtube-playlist-create`](../youtube-playlist-create/SKILL.md) — base skill for creating new playlists
- [`youtube-channel-video-organize`](../youtube-channel-video-organize/SKILL.md) — composer that adds videos to playlists during channel organization
- [`youtube-video-snippet-update`](../youtube-video-snippet-update/SKILL.md) — base skill for updating video title/description/tags (often paired in backfill workflows)
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — composer that adds videos to playlists after upload
