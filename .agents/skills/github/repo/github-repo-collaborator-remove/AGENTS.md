# Repo Collaborator Remove — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You must revoke one user's collaborator access across a repo set after a
  transfer or cutover.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/github/repo/github-repo-collaborator-remove/scripts

python3 "$SCRIPTS"/remove-repo-collaborators.py --owner <owner> --collaborator <login> --repos a,b
python3 "$SCRIPTS"/remove-repo-collaborators.py --owner <owner> --collaborator <login> --repos a,b --execute
```

Exit codes: `0` all removed/planned · `1` failure · `2` config error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`github-repo-transfer-verify`](../../transfer/github-repo-transfer-verify/SKILL.md)
  — verify transfers before revoking interim access.
