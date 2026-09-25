# PR Merge Decision Classifier — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational
SSOT resides in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are about to merge a reviewed pull request and want a deterministic, model-backed
  MERGE/HOLD gate before merging.
- You want a System One (Laya/Jev) typed-decision classification of a PR built from
  read-only `gh` state.
- You want optional auto-merge that runs only on a `MERGE` verdict, with a fixed command
  and no bypass flags.
- You need explicit numeric thresholds (confidence ≥ 0.9, risk ≤ 0.5) instead of prose
  judgement.

Do NOT use this skill for free-form review text, for merging without a review verdict, or
to override a backend error — errors never mean approval.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates,
scripts, and verification steps. Do NOT execute any step without first loading `SKILL.md` —
this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — operational SSOT (CLI contract, gate semantics, prohibited actions)
- [`scripts/classify-pr.py`](scripts/classify-pr.py) — deterministic classifier core
- [`scripts/laya-server.bash`](scripts/laya-server.bash) — local Laya server manager
- [`CHANGELOG.md`](CHANGELOG.md) — release history
- [`TRACEABILITY.md`](TRACEABILITY.md) — provenance and session records
- [`opencode-jsonc-util`](../../../opencode-jsonc-util/SKILL.md) — JSONC provider base-URL resolution
- [`github-repo-commit-fetch`](../../../github-repo-commit-fetch/SKILL.md) — read-only repository fetch primitives
- [`mise-tool-management`](../../../mise-tool-management/SKILL.md) — runtime tool resolution
- [`skill-factory`](../../../skill-factory/SKILL.md) — skill creation protocol
