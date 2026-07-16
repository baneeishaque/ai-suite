# YouTube Video Metadata Update — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to update YouTube video metadata after upload — category, embeddable setting, made-for-kids label, license, language, public stats visibility, containsSyntheticMedia, or age restriction.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including credential management via [`google-oauth-setup`](../google-oauth-setup/SKILL.md) and the video update script with all flag options. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`google-oauth-setup`](../google-oauth-setup/SKILL.md) — base skill for OAuth credential lifecycle
- [`youtube-video-snippet-update`](../youtube-video-snippet-update/SKILL.md) — complementary base skill for title/description/tags updates
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — composer that invokes this skill as a post-upload step
- [`youtube-playlist-list`](../youtube-playlist-list/SKILL.md) — base skill for playlist listing
- [`media-audio-language-detect`](../media-audio-language-detect/SKILL.md) — base skill that provides the detected language code used for `--language`
