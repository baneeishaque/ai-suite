# Transfer Completion Poll — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- Transfers have been accepted and you must wait until the repos appear under
  the destination owner.
- You need a landed/pending summary for the run report.
- You need per-attempt evidence of the landing wait.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/github/transfer/github-repo-transfer-completion-poll/scripts

python3 "$SCRIPTS"/poll-transfer-completion.py --destination-owner <login> --repos a,b
```

Exit codes: `0` all landed · `1` pending · `2` config error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`github-api-poll-until`](../../github-api-poll-until/SKILL.md) — the base this stage wraps.
- [`github-repo-transfer-verify`](../github-repo-transfer-verify/SKILL.md) — the next stage.
