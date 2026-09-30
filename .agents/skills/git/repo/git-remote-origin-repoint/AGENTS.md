# Git Remote Origin Repoint — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- Local clones must follow repositories that moved to a new owner; origin
  URLs need batch repointing with verification.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/git/repo/git-remote-origin-repoint/scripts

python3 "$SCRIPTS"/repoint-origin-remotes.py --clones-root <dir> --new-owner <owner> --repos a,b
python3 "$SCRIPTS"/repoint-origin-remotes.py --clones-root <dir> --new-owner <owner> --repos a,b --execute
```

Exit codes: `0` all verified/planned · `1` failure · `2` config error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`github-repo-transfer-verify`](../../../github/transfer/github-repo-transfer-verify/SKILL.md)
  — verify the server-side transfer first.
