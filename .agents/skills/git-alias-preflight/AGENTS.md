# Git Alias Preflight — Companion Bridge

## Purpose

This file is the companion bridge for the
[`git-alias-preflight`](SKILL.md) general infrastructure skill.
It exists so non-skill-aware agent runtimes discover this skill exists.
The operational Single Source of Truth lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Apply when a repository needs git aliases that run a pre-flight check
before the real command. The canonical use case is `git status` that
first runs a change-detection gate, prints the result, then shows the
real working-tree status. The alias pattern uses git's `!` shell
prefix with a dispatch script that `exec`s the real command on fallthrough.

Do NOT apply when the task is configuring the check itself (use a
domain composer like `claude-config-change-gate`) or setting up the
hook chain (use `git-repo-hook-chain`).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [SKILL.md](SKILL.md) — the SSOT
- [`git-repo-hook-chain`](../git-repo-hook-chain/SKILL.md) — companion dispatch that the alias invokes
- [`git-operation-blocking-hooks`](../git-operation-blocking-hooks/SKILL.md) — composer that integrates this
  alias into the blocking gate
