# opencode-session-log-cleanup — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to remove opencode logger-plugin session logs for a specific
  session ID.
- You want explicit user verification before any log files are deleted.
- You need the removal to use the system trash when available, with
  post-deletion verification that no artifacts remain.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`safe-file-cleanup`](../../general/file/safe-file-cleanup/SKILL.md) — base primitive invoked by this skill.
- [`opencode-current-session-id`](../opencode-current-session-id/SKILL.md) — sibling; resolves the current session
ID/title from logger logs.
