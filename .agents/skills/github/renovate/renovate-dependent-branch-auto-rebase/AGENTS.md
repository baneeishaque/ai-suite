# Renovate Dependent Branch Auto-Rebase — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT resides in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You want to ensure Renovate branches follow the base branch after a rewrite
- You want a unified workflow: Renovate auto-rebase when configured, manual cascade fallback otherwise
- You want to automate the decision: let Renovate handle it, or fall back to manual restack

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`renovate-config-patterns`](../renovate-config-patterns/SKILL.md) — base skill for config generation
- [`renovate-auto-rebase-detector`](../renovate-auto-rebase-detector/SKILL.md) — base skill for detection
- [`git-dependent-branch-restack-cascade`](../../git/branch/dependent-branch-restack-cascade/SKILL.md) — manual restack fallback