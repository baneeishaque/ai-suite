# Git Submodule History Removal — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to remove a submodule from a repository's complete history
  (INTRO + POINTER-UPDATE commits dropped via a scripted, worktree-isolated
  rebase).
- You need the pre-rewrite classification, the refresh-1 audited cleanup
  set, the refresh-2 baseline verification, and the gated push sequence for
  a submodule purge.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full eleven-gate operational procedure.
Do NOT execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`scripts/plan-removal.py`](scripts/plan-removal.py) — deterministic
  discovery half (classification + gate emission).
