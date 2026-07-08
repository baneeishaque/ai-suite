# Git Repo Hook Chain — Companion Bridge

## Purpose

This file is the companion bridge for the
[`git-repo-hook-chain`](SKILL.md) general infrastructure skill.
It exists so non-skill-aware agent runtimes discover this skill exists.
The operational Single Source of Truth lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Apply when setting up repo-level git hooks that need a standardized
dispatch pattern: `core.hooksPath` pointing at `scripts/githooks/`,
`lib.bash` as a single entry point that dispatches by caller name, and
thin wrappers for `pre-commit`, `pre-push`, `pre-merge-commit`, and
`pre-rebase`. The check logic itself is injected via the
`GATE_CHECK_SCRIPT` environment variable, set by a domain composer.

Do NOT apply when the task is the global hook infrastructure (use
`git-global-hook-bootstrap`) or defining the check logic itself
(use a domain composer like `claude-config-change-gate`).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [SKILL.md](SKILL.md) — the SSOT
- [`git-global-hook-bootstrap`](../git-global-hook-bootstrap/SKILL.md) — upstream global hook that triggers repo bootstrap
- [`git-alias-preflight`](../git-alias-preflight/SKILL.md) — companion alias that invokes same lib.bash dispatch
- [`git-operation-blocking-hooks`](../git-operation-blocking-hooks/SKILL.md) — composer integrating all three
