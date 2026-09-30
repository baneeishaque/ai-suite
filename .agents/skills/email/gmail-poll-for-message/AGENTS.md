# Gmail Poll For Message — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- The mailbox to watch is Gmail and you need to wait for a matching email with a
  bounded attempt budget.
- You want the Gmail endpoint and app-password conventions applied without
  remembering them per call.
- You need the offline fixture passthrough for testing Gmail-wait logic.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/email/gmail-poll-for-message/scripts

GMAIL_APP_PASSWORD='<app-password>' python3 "$SCRIPTS"/poll-gmail-message.py \
    --username <gmail-address> --subject-contains <text>
```

Exit codes: `0` arrived · `1` exhausted · `2` config error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`email-poll-for-message`](../email-poll-for-message/SKILL.md) — the base composite this preset invokes.
- [`gmail-event-email-to-ics`](../../calendar/gmail-event-email-to-ics/SKILL.md) — complementary Gmail workflow.
