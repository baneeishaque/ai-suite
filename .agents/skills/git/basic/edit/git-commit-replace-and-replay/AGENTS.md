# Git Commit Replace and Replay — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to replace exactly one commit (content edit, reword, or author
  change) and replay its descendants — non-interactively, without a rebase
  todo writer.
- You are a composer wiring Mode B (dedicated-worktree in-place) mechanics
  or pairing a replacement with byte-level fingerprint verification.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
the `prepare`/`finish`/`verify` CLI contract, state JSON schema, the
range-diff marker accounting rule (at most one changed commit), autostash
semantics, and the conflict recovery path (exit 3). Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`git-commit-edit-in-worktree`](../git-commit-edit-in-worktree/SKILL.md)
  — primary composer (Mode B delegates here).
- [`git-commit-edit`](../../../../git-commit-edit/SKILL.md) — interactive
  alternative route.
- [`git-worktree-state-fingerprint`](../../audit/git-worktree-state-fingerprint/SKILL.md)
  — byte-level verification companion.
- [`git-pre-execution-safety-stash`](../../../../git-pre-execution-safety-stash/SKILL.md)
  — recoverable snapshot before the replacement.
