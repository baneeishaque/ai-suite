# YouTube Channel Video Organize — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to organize existing YouTube videos into playlists — for example, after uploading several videos over time and wanting to sort them into topic-specific playlists, or when performing a channel content audit and restructuring.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including credential management via [`google-oauth-setup`](../google-oauth-setup/SKILL.md), listing videos and playlists, creating playlists, and assigning videos. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`google-oauth-setup`](../google-oauth-setup/SKILL.md) — base skill for OAuth credential lifecycle
- [`youtube-channel-video-list`](../youtube-channel-video-list/SKILL.md) — base skill for listing all channel videos
- [`youtube-playlist-list`](../youtube-playlist-list/SKILL.md) — base skill for listing existing playlists
- [`youtube-playlist-create`](../youtube-playlist-create/SKILL.md) — base skill for creating new playlists
- [`youtube-playlist-item-add`](../youtube-playlist-item-add/SKILL.md) — base skill for adding videos to playlists
- [`youtube-video-snippet-update`](../youtube-video-snippet-update/SKILL.md) — base skill for updating video title/description/tags (complementary during organization)
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — composer for uploading new videos (complementary workflow)
