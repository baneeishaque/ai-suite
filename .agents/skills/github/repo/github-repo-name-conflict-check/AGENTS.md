# GitHub Repo Name Conflict Check — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You must establish that candidate repository names are free under a GitHub
  owner account before naming something (new repo, transfer destination).
- You need per-name verdicts that see private repositories (authenticated owner-token lookup, not a public listing).
- You need the owner's total repo count alongside per-name verdicts (`--enumerate`).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/github/repo/github-repo-name-conflict-check/scripts

python3 "$SCRIPTS"/check-name-conflicts.py --owner <owner> --repos a,b,c --token-user <login>
```

Exit codes: `0` all available · `1` taken/unknown present · `2` usage error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`github-repo-transfer-destination-conflict-check`](../../transfer/github-repo-transfer-destination-conflict-check/SKILL.md)
  — transfer composite over this base.
- [`gh-repo-create`](../../../gh-repo-create/SKILL.md) — repo creation; this skill is its pre-flight reference.
