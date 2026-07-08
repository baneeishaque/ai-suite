# GitHub PR Edit — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives
in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to update an existing PR's title or description to match project conventions.
- You edited a PR's branch and need to reflect the changes in the PR metadata.
- You need to view current PR details (title, body, head ref, state) before editing.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all environment setup, script invocation
commands, and the GitHub API fallback. Do NOT execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [`git-github-auth-fallback`](../git-github-auth-fallback/SKILL.md) — when `gh` CLI is not authenticated
- [`github-rest-api-fallback`](../github-rest-api-fallback/SKILL.md) — REST API alternative for PR mutations
- `table-persistence-implementation` — known composer in the `acers-web` repository (private)
