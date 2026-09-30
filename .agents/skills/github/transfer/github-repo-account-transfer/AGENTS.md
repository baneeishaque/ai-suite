# Account Transfer — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are orchestrating a full account-to-account repository transfer
  (gate -> baseline -> initiate -> acceptance -> wait -> verify -> cleanup ->
  repoint) or resuming it at any stage.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/github/transfer/github-repo-account-transfer/scripts

python3 "$SCRIPTS"/run-account-transfer.py gate --destination-owner <dest> --repos a,b
python3 "$SCRIPTS"/run-account-transfer.py initiate --old-owner <old> --destination-owner <dest> --repos a,b --execute
# (destination accepts the confirmation email)
python3 "$SCRIPTS"/run-account-transfer.py wait --destination-owner <dest> --repos a,b
python3 "$SCRIPTS"/run-account-transfer.py verify --baseline baseline.json --old-owner <old> --destination-owner <dest>
```

Exit codes: child stage's exit code (`0`/`1`/`2`).

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`github-repo-transfer-verify`](../github-repo-transfer-verify/SKILL.md)
  — the closing verification stage.
- [`email-poll-for-message`](../../../email/email-poll-for-message/SKILL.md)
  — optional proactive acceptance-email wait.
