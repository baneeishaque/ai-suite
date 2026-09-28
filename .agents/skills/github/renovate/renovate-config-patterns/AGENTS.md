# Renovate Config Patterns — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT resides in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to generate a Renovate configuration file from a template (base, automerge, monorepo, docker, python)
- You need to produce a Renovate config with specific settings (auto-rebase, auto-merge, monorepo, etc.)
- You are composing a higher-level workflow that requires Renovate config generation

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`renovate-auto-rebase-detector`](../renovate-auto-rebase-detector/SKILL.md) — consumes generated configs to detect auto-rebase behavior
- [`renovate-dependent-branch-auto-rebase`](../renovate-dependent-branch-auto-rebase/SKILL.md) — composer that uses this base for config generation
- [`github-workflow-renovate`](../github-workflow-renovate/SKILL.md) — future composer for GitHub Actions workflow generation