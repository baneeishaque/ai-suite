# GitHub Repo Edit Metadata — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to set or update a repository's description.
- You need to add or remove repository topics.
- You are automating post-publish metadata configuration.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all environment setup, script invocation commands, and the no-op guard. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`gh-repo-create`](../gh-repo-create/SKILL.md) — create the repo before editing its metadata
- [`github-repo-publish`](../github-repo-publish/SKILL.md) — top-level composer that chains create + template + metadata
- [`github-sync`](../github-sync/SKILL.md) — automated metadata sync via CI workflow
