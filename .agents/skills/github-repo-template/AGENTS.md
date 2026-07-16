# GitHub Repo Template — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to generate the full repository template including community standards, `.github/` structure, and MaC maturity markers.
- A higher-level publish orchestrator requires a complete template set.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including script invocation with `--owner`, `--repo-name`, `--output-dir`, and `--maturity`. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`github-repo-publish`](../github-repo-publish/SKILL.md) — C7 orchestrator that calls this skill
- [`github-repo-templates`](../github-repo-templates/SKILL.md) — C1 composer for template subset
- [`github-docs`](../github-docs/SKILL.md) — C5 composer for docs subset
