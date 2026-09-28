# Renovate Auto-Rebase Detector — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT resides in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to determine if a Renovate config will auto-rebase on base branch rewrite
- You are building a workflow that depends on Renovate's auto-rebase behavior
- You need to decide whether manual restack fallback is needed

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`renovate-config-patterns`](../renovate-config-patterns/SKILL.md) — generates configs this detector analyzes
- [`renovate-dependent-branch-auto-rebase`](../renovate-dependent-branch-auto-rebase/SKILL.md) — composer that uses this detector
- [`git-dependent-branch-restack-cascade`](../../git/branch/dependent-branch-restack-cascade/SKILL.md) — manual restack fallback