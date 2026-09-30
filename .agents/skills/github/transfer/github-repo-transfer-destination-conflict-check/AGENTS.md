# Transfer Destination Conflict Check — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are about to initiate repository transfers and must gate on destination
  name availability.
- You need a single `pass` / `block` verdict plus the blocking repo list.
- You need the per-name evidence behind the gate (streamed JSONL).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/github/transfer/github-repo-transfer-destination-conflict-check/scripts

python3 "$SCRIPTS"/check-destination-conflicts.py --destination-owner <login> --repos a,b
```

Exit codes: `0` pass · `1` block · `2` config error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`github-repo-name-conflict-check`](../../repo/github-repo-name-conflict-check/SKILL.md)
  — the base this gate wraps.
- [`github-repo-transfer-initiate`](../github-repo-transfer-initiate/SKILL.md)
  — the stage that consumes the gate verdict.
