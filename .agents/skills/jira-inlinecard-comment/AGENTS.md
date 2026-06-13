# Jira InlineCard Comment — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives
in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to add a GitHub PR link as an inlineCard (rich card) comment on a Jira issue.
- You need to update an existing Jira comment to use inlineCard format instead of plain text.
- You need to verify that PR links on Jira tickets are correctly rendered as inlineCards.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all environment setup, token retrieval, wiki
markup format, script invocation commands, and ADF verification steps. Do NOT execute any step without first loading
`SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`jira-acli-operations`](../jira-acli-operations/SKILL.md) — CLI-based comment operations (plain text only; does not
produce inlineCard)
- [`jira-automation-rules`](../jira-automation-rules/SKILL.md) — Jira Cloud automation rule construction
- `table-persistence-implementation` — known composer in the `acers-web` repository (private)
