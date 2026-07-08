# GitHub Sync Description — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to sync a GitHub repository description from `README.md` markers.
- You need to create a workflow that parses `<!-- START_DESCRIPTION -->` / `<!-- END_DESCRIPTION -->` blocks.
- You are setting up MaC (Markdown-as-Configuration) for repository metadata.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the MaC marker parsing pattern explanation, script invocation, and the generated YAML output. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`github-sync-topics`](../github-sync-topics/SKILL.md) — companion base skill for topic sync
- [`gh-repo-edit-metadata`](../gh-repo-edit-metadata/SKILL.md) — direct metadata editing via `gh`
