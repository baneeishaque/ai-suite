# GitHub PR Labeler — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to set up automatic PR labeling based on changed file paths.
- You need to create or update a `labeler-config.yml` with label-to-glob mappings.
- You are configuring CI/CD for a repository and want PRs auto-labeled.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the explanation of why the workflow and config files are coupled, the label mapping table, and script invocation. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`github-workflow-creation`](../github-workflow-creation/SKILL.md) — general workflow authoring
- [`github-ci-markdown-lint`](../github-ci-markdown-lint/SKILL.md) — companion CI workflow
- [`github-ci-python-lint`](../github-ci-python-lint/SKILL.md) — companion CI workflow
