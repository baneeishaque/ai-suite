# TypeScript Import Formatting Skill — Companion Bridge

## Purpose

This file is the companion bridge for the `TypeScript Import Formatting` skill. It exists for non-skill-aware runtimes and points them to the operational SSOT in [`SKILL.md`](./SKILL.md).

## When This Skill Applies

- When a TypeScript or TSX file has a single-line named import with two or more specifiers.
- When a codebase style update requires multiline named-import blocks for readability.
- When you want a deterministic, script-backed transformation instead of manual import reformatting.

## Operational Procedure

Read [`SKILL.md`](./SKILL.md) for the full operational procedure, including the required script, environment checks, and verification steps. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`skill-factory`](../skill-factory/SKILL.md) — Skill creation protocol for new skills.
- [`code-explanation`](../code-explanation/SKILL.md) — Documentation standards for code readability and style.
