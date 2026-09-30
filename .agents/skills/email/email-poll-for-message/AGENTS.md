# Email Poll For Message — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You must wait until a matching email arrives (transfer confirmation,
  verification, 2FA) with a bounded attempt budget.
- You need provider-agnostic mailbox access (IMAP) with criteria filters
  (subject/from/unseen) and JSONL match records.
- You need to test mailbox-waiting logic offline against a fixture file.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/email/email-poll-for-message/scripts

EMAIL_PASSWORD='<app-password>' python3 "$SCRIPTS"/poll-email-message.py \
    --imap-host <host> --username <user> --subject-contains <text>
```

Exit codes: `0` arrived · `1` exhausted · `2` config error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`poll-until`](../../general/polling/poll-until/SKILL.md) — the base engine this composite invokes.
- [`gmail-poll-for-message`](../gmail-poll-for-message/SKILL.md) — Gmail preset over this skill.
