# Transfer Initiate — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are initiating repository transfers after the destination gate passed.
- You need a dry-run plan of the POST requests before executing.
- You need the acceptance-step contract (email-based, 1-day expiry).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/github/transfer/github-repo-transfer-initiate/scripts

# dry-run (default):
python3 "$SCRIPTS"/initiate-repo-transfers.py --old-owner <old> --destination-owner <dest> --repos a,b
# live:
python3 "$SCRIPTS"/initiate-repo-transfers.py --old-owner <old> --destination-owner <dest> --repos a,b --execute
```

Exit codes: `0` all accepted/planned · `1` failure · `2` config error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`github-repo-transfer-destination-conflict-check`](../github-repo-transfer-destination-conflict-check/SKILL.md)
  — the gate that must pass before initiation.
- [`email-poll-for-message`](../../../email/email-poll-for-message/SKILL.md)
  — waits for the acceptance email.
