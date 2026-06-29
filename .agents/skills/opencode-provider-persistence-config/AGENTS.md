# opencode Provider Persistence Configuration — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes that
auto-load `AGENTS.md` by filename convention. The operational SSOT lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

- An OpenCode provider API key saved via `/connect` does not survive a restart
  of the application.
- The provider's models were available in the current session but disappear
  after quitting and relaunching OpenCode.
- A team member reports having to re-authenticate every session.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
credential storage model, the startup registration gap, the config declaration
requirement, and the troubleshooting table. Do NOT execute any step without
first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`opencode-permission-config`](../opencode-permission-config/SKILL.md) —
  OpenCode permission configuration (complementary domain).
- [OpenCode Docs — Providers](https://opencode.ai/docs/providers/) — Official
  OpenCode documentation for provider setup.
