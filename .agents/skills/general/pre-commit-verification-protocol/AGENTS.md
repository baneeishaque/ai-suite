# Pre-Commit Verification Protocol — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- After creating or modifying any SKILL.md file.
- Before staging changes to skill or rule files.
- Before declaring a skill-doc edit done.
- Any time the [`skill-factory`](../../skill-factory/SKILL.md)
  Post-Drafting Checklist or Skill Enrichment Workflow requires
  pre-commit verification.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full 4-step protocol:
cross-reference audit → markdown lint → visual smoke test → final
status check. Do NOT skip any step unless the When to Skip section
explicitly allows it.

## Cross-References

- [`skill-cross-reference-audit`](../skill-cross-reference-audit/SKILL.md)
  — consumed in Step 1.
- [`markdown-lint-workflow`](../markdown-lint-workflow/SKILL.md)
  — consumed in Step 2.
- [`skill-factory`](../../skill-factory/SKILL.md) — consumer of this
  protocol.
- [`planning-artifact-lifecycle`](../planning-artifact-lifecycle/SKILL.md)
  — companion base skill.
