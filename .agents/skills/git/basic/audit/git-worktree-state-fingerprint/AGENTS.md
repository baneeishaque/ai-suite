# Git Worktree State Fingerprint — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need byte-level proof that a Git worktree's state (index, staged diff,
  worktree diff, untracked set, HEAD, commit count) was unchanged across an
  operation — or a precise list of what changed.
- You are verifying a history rewrite, a stash lifecycle step, or any
  operation that must not disturb the surrounding working-tree bytes.
- You are a composer (e.g. `git-commit-edit-in-worktree`) wiring baseline
  capture/compare gates around a mutation.
- You need to prove a commit left a pre-existing dirty state undisturbed —
  reconstruct the pre-state from its saved patch and diff named files against
  the live worktree with `scripts/reconstruct-baseline-diff.py`.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
the capture/compare CLI contract, the fingerprint field table, hash-parity
semantics, and the expected-delta policy rules. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`git-commit-edit-in-worktree`](../../edit/git-commit-edit-in-worktree/SKILL.md)
  — primary composer (Gates 1 and 8).
- [`git-commit-replace-and-replay`](../../edit/git-commit-replace-and-replay/SKILL.md)
  — in-place replacement primitive whose verification pairs with this
  fingerprint.
- [`git-pre-execution-safety-stash`](../../../../git-pre-execution-safety-stash/SKILL.md)
  — recoverable snapshot sibling; this skill is read-only evidence.
- [`git-worktree-snapshot-nonintrusive`](../../../snapshot/git-worktree-snapshot-nonintrusive/SKILL.md)
  — restorable worktree snapshot (complementary: "can be restored" vs "nothing changed").
- [`git-pre-execution-safety-snapshot`](../../../snapshot/git-pre-execution-safety-snapshot/SKILL.md)
  — composer capturing a restorable safety snapshot; pair with this fingerprint
  to prove capture non-intrusiveness.
