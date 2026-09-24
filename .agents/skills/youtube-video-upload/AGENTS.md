# YouTube Video Upload — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to upload a video to YouTube with full metadata (title, description, tags, language, recording date) and optionally add it to a playlist. This skill orchestrates the entire workflow: pre-processing, authentication, playlist selection, upload via CLI, and post-upload verification.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure. This skill composes multiple base skills — load all of the following alongside this one before executing any step: [`google-oauth-setup`](../google-oauth-setup/SKILL.md) (OAuth), [`youtube-playlist-list`](../youtube-playlist-list/SKILL.md) (playlist selection), [`media-audio-language-detect`](../media-audio-language-detect/SKILL.md) (language auto-detection), [`youtube-video-snippet-update`](../youtube-video-snippet-update/SKILL.md) (post-upload snippet correction), [`youtube-video-metadata-update`](../youtube-video-metadata-update/SKILL.md) (post-upload API fields), [`url-shortcut-creator`](../url-shortcut-creator/SKILL.md) (bookmark file), [`youtube-studio-settings`](../youtube-studio-settings/SKILL.md) (Studio-only settings), [`lower-case-hyphen-naming`](../lower-case-hyphen-naming/SKILL.md) (optional file rename), [`ffmpeg-lossless-concat`](../ffmpeg-lossless-concat/SKILL.md) (optional video merge), [`webm-recording-merge-with-filler`](../webm-recording-merge-with-filler/SKILL.md) (optional segment merge). Do NOT execute any step without first loading all of these `SKILL.md` files — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`google-oauth-setup`](../google-oauth-setup/SKILL.md) — base skill for OAuth credential lifecycle
- [`youtube-playlist-list`](../youtube-playlist-list/SKILL.md) — base skill for playlist listing
- [`media-audio-language-detect`](../media-audio-language-detect/SKILL.md) — base skill for language auto-detection
- [`youtube-video-metadata-update`](../youtube-video-metadata-update/SKILL.md) — base skill for post-upload metadata
- [`youtube-video-snippet-update`](../youtube-video-snippet-update/SKILL.md) — base skill for post-upload snippet correction (title, description, tags)
- [`url-shortcut-creator`](../url-shortcut-creator/SKILL.md) — base skill for URL bookmark files
- [`ffmpeg-lossless-concat`](../ffmpeg-lossless-concat/SKILL.md) — optional pre-upload video merging
- [`webm-recording-merge-with-filler`](../webm-recording-merge-with-filler/SKILL.md) — optional pre-upload recorded segment merging
- [`lower-case-hyphen-naming`](../lower-case-hyphen-naming/SKILL.md) — optional file naming standardization
