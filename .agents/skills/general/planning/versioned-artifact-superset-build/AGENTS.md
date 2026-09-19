# Versioned Artifact Superset Build — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

- Creating version n+1 of ANY versioned markdown artifact (implementation-plan, commit-preview, walkthrough,
  audit-log, summary, skill doc) under the Verbatim-Superset Construction convention.
- A new artifact version must provably contain the previous version's text byte-identical (`--verify`).

## Operational Procedure

Read [`SKILL.md`](SKILL.md), then invoke `scripts/build-version-superset.py --old <vN> --new <vN+1> --deltas
<deltas.md> [--change-history-row "…"]` — optionally `--dry-run` first, then `--verify` immediately after the build.
Do NOT re-derive the copy-and-append logic ad-hoc — this bridge is intentionally non-actionable.

## Cross-References

- [`planning-version-coverage-audit`](../planning-version-coverage-audit/SKILL.md) — verification-side companion
(post-hoc FULL/PARTIAL/MISSING gate; run after construction).
- [`planning-artifact-lifecycle`](../planning-artifact-lifecycle/SKILL.md) — lifecycle protocol that composes this
skill as the Step 3 construction half.
- [`planning-artifact-naming`](../planning-artifact-naming/SKILL.md) — naming convention (§2.2 versioning rules)
for the artifacts this skill versions.
- [`planning-superseded-version-retirement`](../planning-superseded-version-retirement/SKILL.md) — downstream
consumer of FULL coverage, unlocking authorized retirement.
