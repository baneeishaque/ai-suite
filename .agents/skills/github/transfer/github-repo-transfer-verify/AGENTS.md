# Transfer Verify — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to prove a completed transfer: old owner missing all repos,
  destination owner ok all repos (SHA-level equality).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/github/transfer/github-repo-transfer-verify/scripts

python3 "$SCRIPTS"/verify-repo-transfer.py --baseline <snapshot.json> \
    --old-owner <old> --destination-owner <dest>
```

Exit codes: `0` pass · `1` fail · `2` config error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`github-repo-transfer-baseline-capture`](../github-repo-transfer-baseline-capture/SKILL.md)
  — produces the baseline snapshot.
- [`github-repo-state-fingerprint`](../../repo/github-repo-state-fingerprint/SKILL.md)
  — the composed base skill.
