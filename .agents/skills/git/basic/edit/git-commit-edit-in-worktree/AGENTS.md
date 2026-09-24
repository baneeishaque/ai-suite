# Git Commit Edit In Worktree — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to drop, amend, reword, or edit a commit in history while the
  current working tree is dirty and MUST stay untouched.
- You need a scripted (non-interactive) rebase inside an isolated `git
  worktree`, with byte-level baseline verification of the untouched main
  worktree.
- You are planning a submodule history removal that delegates its rebase
  mechanics here.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
the nine-gate protocol, baseline evidence capture, and fast-forward rules.
Do NOT execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`git-rebase-drop-noninteractive`](../git-rebase-drop-noninteractive/SKILL.md) —
  base skill providing the todo-writer invoked as `GIT_SEQUENCE_EDITOR`.
- [`git-submodule-history-classification`](../../../../git/submodule/repair/
  git-submodule-history-classification/SKILL.md) —
  base skill providing commit classification for scoping.
- [`git-submodule-history-removal`](../../../../git/submodule/lifecycle/
  git-submodule-history-removal/SKILL.md) —
  composer built on top of this skill.
- [`git-pre-execution-safety-stash`](../../../../git-pre-execution-safety-stash/SKILL.md) —
  optional safety stash at the backup gate.
