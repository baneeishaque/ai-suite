# YouTube Video Snippet Update — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to update an existing YouTube video's title, description, or tags — for example, to fix a
typo in the title after upload, to standardize naming conventions during channel tidying, or to add
description text to a batch of previously uploaded videos.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including credential management via
[`google-oauth-setup`](../google-oauth-setup/SKILL.md) and the video snippet update script with all
flag options. Do NOT execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`google-oauth-setup`](../google-oauth-setup/SKILL.md) — base skill for OAuth credential lifecycle
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — composer that may invoke this skill
  for post-upload correction
- [`youtube-video-metadata-update`](../youtube-video-metadata-update/SKILL.md) — complementary base
  skill for advanced metadata (category, language, embeddable, etc.)
- [`youtube-playlist-item-add`](../youtube-playlist-item-add/SKILL.md) — base skill for adding
  videos to playlists (often paired in backfill workflows)
- [`youtube-channel-video-organize`](../youtube-channel-video-organize/SKILL.md) — composer that may
  invoke both snippet update and playlist item add during channel organization
