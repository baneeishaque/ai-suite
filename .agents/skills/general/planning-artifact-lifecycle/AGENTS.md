# Planning Artifact Lifecycle — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- When creating or versioning any planning artifact.
- When user asks to delete or clean up planning artifacts.
- When CAM §7.1 enforcement is required before creating a new version.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full lifecycle: creation →
versioning triggers → CAM §7.1 enforcement → presentation & approval →
deletion → fresh start protocol. Do NOT skip the CAM §7.1 step before
creating a new version.

## Cross-References

- [`planning-artifact-naming`](../planning-artifact-naming/SKILL.md) —
  naming convention (companion base skill).
- [`pre-commit-verification-protocol`](../pre-commit-verification-protocol/SKILL.md)
  — verification pipeline for artifact-related changes.
- [`skill-factory`](../../skill-factory/SKILL.md) — consumed when
  creating skill-creation-plan or skill-documentation-plan artifacts.
