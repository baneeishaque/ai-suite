# OpenCode AGENTS.md Manager — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- When AGENTS.md contains rows from multiple sessions and only the
  current session's rows should be committed.
- After creating or enriching a skill that needs registration in
  AGENTS.md.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full workflow: detect changes →
isolate rows via `git add -p` → verify isolation → commit →
post-commit verification.

## Cross-References

- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  — base skill for staging and atomic commit construction.
- [`pre-commit-verification-protocol`](../general/pre-commit-verification-protocol/SKILL.md)
  — verification pipeline.
- [`skill-factory`](../skill-factory/SKILL.md) — skill creation workflow.
