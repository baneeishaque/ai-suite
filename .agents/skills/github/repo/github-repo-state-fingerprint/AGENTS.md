# GitHub Repo State Fingerprint — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You must snapshot repository state before a state-changing operation and prove
  it unchanged afterward (transfer, rename, settings change).
- You need a deterministic `ok` / `drift` / `missing` / `error` verdict per
  repository instead of a noisy raw API JSON diff.
- You need a cross-owner comparison (same repo names, different owner).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI
contract, output schema, and exit codes. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Quick Reference

```bash
SCRIPTS=.agents/skills/github/repo/github-repo-state-fingerprint/scripts

python3 "$SCRIPTS"/repo-state-fingerprint.py capture --owner <login> --repos a,b --output baseline.json
python3 "$SCRIPTS"/repo-state-fingerprint.py compare --baseline baseline.json --owner <other-owner>
```

Exit codes: `0` clean · `1` drift/missing/error · `2` usage error.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`github-repo-transfer-baseline-capture`](../../transfer/github-repo-transfer-baseline-capture/SKILL.md)
  — transfer composite wrapping `capture`.
- [`github-repo-transfer-verify`](../../transfer/github-repo-transfer-verify/SKILL.md)
  — transfer composite wrapping `compare`.
