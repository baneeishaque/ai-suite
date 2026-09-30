# Poll Until — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to wait for an external condition (API state, email arrival, marker file, process result) with a bounded budget.
- You are authoring or maintaining a composer that needs a reusable retry-until loop instead of an ad-hoc sleep loop.
- You need a machine-readable per-attempt timeline (JSONL) plus a final met/exhausted verdict.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/general/polling/poll-until/scripts

python3 "$SCRIPTS"/poll-until.py --interval 10 --attempts 12 -- <check-cmd> [args...]
```

Exit codes: `0` met · `1` exhausted · `2` usage error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`github-api-poll-until`](../../../github/github-api-poll-until/SKILL.md) — GitHub API composite over this engine.
- [`email-poll-for-message`](../../../email/email-poll-for-message/SKILL.md) — mailbox composite over this engine.
- [`github-repo-transfer-completion-poll`](../../../github/transfer/github-repo-transfer-completion-poll/SKILL.md)
  — transfer-completion composite over the GitHub API layer.
