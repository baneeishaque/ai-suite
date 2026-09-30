# GitHub API Poll Until — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You must wait until a GitHub API endpoint per item reaches an expected HTTP
  status, with a bounded attempt budget.
- You need per-attempt JSONL evidence plus a per-item met/unmet summary.
- You are authoring a higher-level waiter (e.g., transfer-completion poll) over
  the GitHub API.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/github/github-api-poll-until/scripts

python3 "$SCRIPTS"/poll-api-until.py --endpoint 'repos/<owner>/{item}' --items a,b --expect 200
```

Exit codes: `0` all met · `1` any unmet · `2` usage error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`poll-until`](../../general/polling/poll-until/SKILL.md) — the base engine this composite invokes.
- [`github-repo-transfer-completion-poll`](../transfer/github-repo-transfer-completion-poll/SKILL.md)
  — transfer composite over this skill.
