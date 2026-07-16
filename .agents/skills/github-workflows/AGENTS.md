# GitHub Workflows — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to generate all GitHub Actions workflows (lint, PR labeler, sync).
- A higher-level orchestrator requires the full workflow set for a repository.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
script invocation with `--output-dir`. Do NOT execute any step without first
loading `SKILL.md`.

## Cross-References

- [`github-repo-publish`](../github-repo-publish/SKILL.md) — C7 orchestrator that calls this skill
- [`github-ci-lint`](../github-ci-lint/SKILL.md) — C2 composer for lint workflows subset
- [`github-sync`](../github-sync/SKILL.md) — C3 composer for sync workflows subset
