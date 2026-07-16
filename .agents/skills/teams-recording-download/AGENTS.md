# Teams Recording Download — Companion Bridge

## Purpose

This companion bridge exposes the `teams-recording-download` skill to
non-skill-aware agent runtimes. The operational SSOT lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

- User needs to download a Microsoft Teams meeting recording
- User provides meeting date and topic keyword
- Recording is view-only (no direct download button available)
- User wants to save Teams recording as a local MP4 file
- Workflow involves Calendar or Chat meeting search

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`browser-network-interception`](../browser-network-interception/SKILL.md) — base skill for capturing video manifest URLs
- [`video-download-manifest`](../video-download-manifest/SKILL.md) — base skill for downloading video via ffmpeg
- `youtube-studio-settings` (public `ai-suite` repo) — similar browser automation pattern for YouTube Studio
