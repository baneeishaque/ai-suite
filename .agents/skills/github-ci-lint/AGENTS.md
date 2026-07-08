# GitHub CI Lint — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to generate CI lint workflows for GitHub Actions (markdown and Python linting).
- A higher-level workflow composer requires lint workflows.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including script invocation with `--output-dir`. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`github-workflows`](../github-workflows/SKILL.md) — C4 composer that includes lint workflows
- [`github-repo-publish`](../github-repo-publish/SKILL.md) — C7 orchestrator
