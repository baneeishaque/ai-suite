# GitHub Repo Structure — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to create the `.github/` directory structure with issue templates and workflow stubs.
- A higher-level repo template composer requires the `.github/` scaffolding.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including script invocation with `--output-dir` and `--dry-run` flags. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`github-repo-template`](../github-repo-template/SKILL.md) — C6 composer that includes this skill
- [`github-repo-publish`](../github-repo-publish/SKILL.md) — C7 orchestrator
