# Git Global Hook Bootstrap — Companion Bridge

## Purpose

This file is the companion bridge for the
[`git-global-hook-bootstrap`](SKILL.md) general infrastructure skill.
It exists so non-skill-aware agent runtimes discover this skill exists.
The operational Single Source of Truth lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Apply when setting up a new developer machine for hook-aware repositories:
symlink `~/.git-hooks/` to the repo's `dotfiles/git-hooks/`, set
`git config --global core.hooksPath`, and ensure every future checkout
auto-bootstraps repo-level hooks. Also apply when onboarding a developer
who needs the global hook infrastructure.

Do NOT apply when the task is configuring repo-level hooks (use
`git-repo-hook-chain`) or defining which checks to run (use the
domain composer, e.g., `claude-config-change-gate`).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [SKILL.md](SKILL.md) — the SSOT
- [`git-repo-hook-chain`](../git-repo-hook-chain/SKILL.md) — configures repo-level hooks (called by post-checkout)
- [`git-alias-preflight`](../git-alias-preflight/SKILL.md) — registers pre-flight check aliases
- [`git-operation-blocking-hooks`](../git-operation-blocking-hooks/SKILL.md) — composer integrating all three general skills
