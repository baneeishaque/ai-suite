# Session Audit Batch Orchestrator — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You have multiple opencode session exports (`.md` files) and need a
  consolidated aggregate audit report covering all of them
- You have pre-existing JSONL audit outputs from separate
  `session-full-change-audit` runs and need to merge them into one
  cross-reference report
- You need per-file session traceability — which sessions touched which
  files — across N session files

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`session-full-change-audit`](../session-full-change-audit/SKILL.md)
  — Per-file audit engine consumed by this batch orchestrator
- [`session-file-ops-audit`](../session-file-ops-audit/SKILL.md)
  — Predecessor composer (bash file ops only)
- [`file-recovery-from-session`](../file-recovery-from-session/SKILL.md)
  — Parallel composer for recovering files from session exports
- [`edit-application-from-session`](../edit-application-from-session/SKILL.md)
  — Parallel composer for replaying edits
