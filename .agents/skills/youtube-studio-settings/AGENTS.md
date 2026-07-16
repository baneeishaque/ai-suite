# YouTube Studio Settings — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to apply YouTube Studio settings to a video that cannot be set via the YouTube Data API: disabling comments, setting 18+ age restriction, disabling subscriber feed notifications, disabling remixing, or setting caption certification to "never aired in US."

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the multi-backend architecture (JXA on macOS, undetected_chromedriver cross-platform, Playwright stealth fallback), one-time setup, and all CLI flags.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [`google-oauth-setup`](../google-oauth-setup/SKILL.md) — base skill for OAuth credential lifecycle (the Studio session uses Chrome's logged-in state rather than OAuth tokens)
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — composer that may invoke this skill as a post-upload step
