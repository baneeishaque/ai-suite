# YouTube Playlist Create — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to create a new YouTube playlist — for example, to organize channel videos by topic, to prepare a target playlist before a video upload, or to set up a content series.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including credential management via [`google-oauth-setup`](../google-oauth-setup/SKILL.md) and the playlist creation script with all flag options. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`google-oauth-setup`](../google-oauth-setup/SKILL.md) — base skill for OAuth credential lifecycle
- [`youtube-playlist-list`](../youtube-playlist-list/SKILL.md) — base skill for listing existing playlists
- [`youtube-playlist-item-add`](../youtube-playlist-item-add/SKILL.md) — base skill for adding videos to a playlist
- [`youtube-channel-video-organize`](../youtube-channel-video-organize/SKILL.md) — composer that creates playlists during channel organization
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — composer that optionally creates playlists during upload
