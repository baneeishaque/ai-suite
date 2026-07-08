# YouTube Channel Video List — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to see every uploaded video on the authenticated YouTube channel — for example, to identify videos that need to be organized into playlists, to produce an inventory of channel content, or to prepare a list of video IDs for bulk metadata updates.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including credential management via [`google-oauth-setup`](../google-oauth-setup/SKILL.md) and the channel video listing script. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`google-oauth-setup`](../google-oauth-setup/SKILL.md) — base skill for OAuth credential lifecycle
- [`youtube-playlist-list`](../youtube-playlist-list/SKILL.md) — base skill for listing playlists
- [`youtube-playlist-item-add`](../youtube-playlist-item-add/SKILL.md) — base skill for adding videos to playlists
- [`youtube-channel-video-organize`](../youtube-channel-video-organize/SKILL.md) — composer that consumes this skill's output for video categorization
