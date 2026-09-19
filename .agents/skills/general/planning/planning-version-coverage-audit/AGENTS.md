# Planning Version Coverage Audit — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

- A user asks whether an old artifact version is entirely covered / superseded by a newer one ("is vN fully covered by
vN+1?").
- Before retiring or deleting any superseded versioned artifact — this audit is the mandatory coverage gate.
- Any review needing a literal, per-section coverage relation between two documents (not a diff).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full procedure: invoke `scripts/audit-version-coverage.py --old <vN> --new <vN+1>
[--json]`, read the per-section COVERED / ENHANCED / DROPPED classification, and act on the FULL / PARTIAL / MISSING
verdict (exit 0 / 1 / 2). Do NOT re-derive the audit logic ad-hoc — this bridge is intentionally non-actionable.

## Cross-References

- [`planning-superseded-version-retirement`](../planning-superseded-version-retirement/SKILL.md) — composer that
consumes this audit as its coverage gate.
- [`planning-artifact-lifecycle`](../planning-artifact-lifecycle/SKILL.md) — lifecycle protocol that decides when an
audit is needed.
- [`planning-artifact-naming`](../planning-artifact-naming/SKILL.md) — naming convention for the audited artifacts.
- [`versioned-artifact-superset-build`](../versioned-artifact-superset-build/SKILL.md) — authoring-side companion that
constructs vN+1 as vN verbatim + deltas; run this audit after that construction as verification.
