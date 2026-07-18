# Browser Network Interception — Companion Bridge

## Purpose

This companion bridge exposes the `browser-network-interception` skill to
non-skill-aware agent runtimes. The operational SSOT lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

- Agent needs to capture network responses from a web page (API calls,
  video manifests, streamed data URLs)
- Agent needs to intercept URLs matching specific patterns while a page
  loads
- Generic browser automation requiring network-level data capture
- Workflow needs to discover hidden API endpoints or media stream URLs

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`video-download-manifest`](../video-download-manifest/SKILL.md) — base skill for downloading video from captured manifest URLs
- [`teams-recording-download`](../teams-recording-download/SKILL.md) — composer skill that uses this base for Teams recording downloads
