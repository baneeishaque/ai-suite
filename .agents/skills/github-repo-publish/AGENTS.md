# GitHub Repo Publish — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to publish a new GitHub repository with full community standards (templates, workflows, docs, MaC markers).
- You need a single orchestrated workflow that creates the repo, populates files, and pushes.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all script invocation flags. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`gh-repo-create`](../gh-repo-create/SKILL.md) — B1 base skill for repo creation
- [`gh-repo-edit-metadata`](../gh-repo-edit-metadata/SKILL.md) — B2 base skill for metadata
- [`github-repo-template`](../github-repo-template/SKILL.md) — C6 composer for template generation
- [`github-workflows`](../github-workflows/SKILL.md) — C4 composer for workflow generation
