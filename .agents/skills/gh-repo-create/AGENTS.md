# GitHub Repo Create — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to create a new GitHub repository from a local directory.
- You need to push an existing local repo to GitHub as a fresh remote.
- A higher-level publish workflow requires repo creation as its first step.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all environment setup, script invocation commands, and exit code handling. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`gh-repo-edit-metadata`](../gh-repo-edit-metadata/SKILL.md) — companion base skill for post-creation metadata
- [`github-repo-publish`](../github-repo-publish/SKILL.md) — top-level composer
- [`git-github-auth-fallback`](../git-github-auth-fallback/SKILL.md) — auth recovery when `gh` is unauthenticated
