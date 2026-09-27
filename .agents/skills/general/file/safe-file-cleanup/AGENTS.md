# safe-file-cleanup — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to safely remove files or directories from disk.
- The system has a trash/recycle-bin command (`trash`, `gio`) and you want
  to avoid permanent deletion.
- You need verified removal with per-path status output and exit-code
  contracts suitable for automation.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
the CLI contract, protocol, edge cases, and verification steps. Do NOT
execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`file-glob-sort-by-mtime`](../file-glob-sort-by-mtime/SKILL.md) — related file-system base primitive.
- [`opencode-session-log-cleanup`](../../../opencode/opencode-session-log-cleanup/SKILL.md) — primary composer that
invokes this skill.
