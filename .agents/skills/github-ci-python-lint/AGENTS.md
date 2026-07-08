# GitHub CI — Python Lint — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to create a GitHub Actions workflow for Python linting with `ruff`.
- You need to configure the runner OS, Python version, or target glob for linting.
- You are bootstrapping CI for a repository containing Python code.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including script invocation, argument reference, and the generated YAML output. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`github-ci-markdown-lint`](../github-ci-markdown-lint/SKILL.md) — Markdown linting CI companion
- [`github-workflow-creation`](../github-workflow-creation/SKILL.md) — general workflow authoring
