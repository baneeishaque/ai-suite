# Video Download from Manifest — Companion Bridge

## Purpose

This companion bridge exposes the `video-download-manifest` skill to
non-skill-aware agent runtimes. The operational SSOT lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

- Agent has captured a video manifest URL (from network interception,
  API response, or manual discovery)
- Agent needs to download a video from an HLS, DASH, or direct URL
  using ffmpeg
- Workflow requires lossless video download without re-encoding
- Any media processing pipeline that needs to fetch video content

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`browser-network-interception`](../browser-network-interception/SKILL.md) — base skill for capturing manifest URLs from network traffic
- [`teams-recording-download`](../teams-recording-download/SKILL.md) — composer skill that uses this base for Teams recording downloads
