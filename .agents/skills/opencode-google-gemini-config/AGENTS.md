# opencode Google Gemini Configuration — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes that
auto-load `AGENTS.md` by filename convention. The operational SSOT lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

- A user connected their Google AI Studio API key in OpenCode via `/connect`,
  but after restarting OpenCode the Google/Gemini models are no longer
  available.
- A Google AI Studio API key needs to be configured for the first time in
  OpenCode.
- A developer wants to automate the setup of Google Gemini models in an
  OpenCode configuration.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
credential setup, the restart-retention bug diagnosis, the config-block fix,
and the environment variable alternative. Do NOT execute any step without
first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`opencode-provider-persistence-config`](../opencode-provider-persistence-config/SKILL.md)
  — Base skill. Owns the OpenCode credential storage model and startup
  registration knowledge that this composer skill builds upon.
- [`opencode-permission-config`](../opencode-permission-config/SKILL.md) —
  OpenCode permission configuration (complementary OpenCode config domain).
- [Google AI Studio API Keys](https://aistudio.google.com/apikey) — Generate
  API keys for Gemini.
