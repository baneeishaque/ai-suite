# Deterministic Artifact In-Place Amendment — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational
SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- A generated report, registry, or index needs a change its generator cannot express, and
  you are deciding whether to re-run the generator or edit the artifact.
- Someone says "rerun only if needed" and you need a defensible rule for "needed".
- A generated artifact was amended and you need to know whether its derived totals still
  agree with it.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the verdict
table, the baseline step, and the downstream-repair obligation. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the regenerate-vs-amend gate.
- [`planning-artifact-lifecycle`](../planning-artifact-lifecycle/SKILL.md) — lifecycle
  and versioning gates for artifacts.
- [`script-over-instruction-decomposition`](../../../script-over-instruction-decomposition/SKILL.md)
  — where deterministic amendment mechanics belong.
