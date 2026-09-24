# Git Submodule History Classification — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to enumerate registered submodules WITH their remote URLs and
  initialization status (the `docs/uninitialized-submodules.md` style
  inventory).
- You need to classify every commit that touched a submodule path as
  INTRO / POINTER-UPDATE / MIXED / REMOVAL before planning a history rewrite.
- You need branch-scoped discovery that skips checkpoint branches
  (`entire/*`, `backup/*`, `backup2/*`).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
both CLI contracts, classification semantics, and guardrails. Do NOT execute
any step without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`git-submodule-history-removal`](../../lifecycle/git-submodule-history-removal/SKILL.md) —
  primary composer that consumes both scripts.
- [`git-commit-edit-in-worktree`](../../../basic/edit/git-commit-edit-in-worktree/SKILL.md) —
  composer that uses the classification for its scoping step.
- [`git-submodule-uninitialized-audit`](../../../../git-submodule-uninitialized-audit/SKILL.md) —
  complementary full reachability audit.
