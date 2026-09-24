# Git Rebase Drop Non-Interactive — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to drop or edit specific commits from history non-interactively,
  via a scripted `GIT_SEQUENCE_EDITOR` rebase-todo rewrite.
- You are composing a workflow that must never open the interactive rebase
  editor (CI, isolated worktrees, batch history refinement).
- You need an idempotent `--check` mode to verify target SHAs exist in the
  todo before mutating it.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
the CLI contract, invocation form, interrupted-rebase recovery, and
`.gitmodules` conflict resolution. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`git-commit-edit`](../../../../git-commit-edit/SKILL.md) — interactive
  counterpart for single-commit edits.
