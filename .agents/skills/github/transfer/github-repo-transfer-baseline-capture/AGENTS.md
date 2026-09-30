# Transfer Baseline Capture — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are about to transfer repositories and must snapshot pre-transfer state
  under the old owner.
- You need the per-repo `head_sha` map for later SHA-preservation assertions.
- You need a named baseline artifact for the verification stage to consume.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/github/transfer/github-repo-transfer-baseline-capture/scripts

python3 "$SCRIPTS"/capture-transfer-baseline.py --old-owner <login> --repos a,b --output baseline.json
```

Exit codes: `0` all captured · `1` missing/error · `2` config error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`github-repo-state-fingerprint`](../../repo/github-repo-state-fingerprint/SKILL.md)
  — the base this stage wraps.
- [`github-repo-transfer-verify`](../github-repo-transfer-verify/SKILL.md)
  — the stage that consumes the snapshot.
