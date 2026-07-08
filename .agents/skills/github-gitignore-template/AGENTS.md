# GitHub Gitignore Template — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to generate a `.gitignore` for a GitHub repository.
- You need to scope the `.gitignore` by project language (Python, Node, generic).
- A higher-level template composer requires a `.gitignore` as part of the template set.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including script invocation commands and flag options. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`github-repo-templates`](../github-repo-templates/SKILL.md) — C1 composer that includes this skill in the template set
- [`github-repo-publish`](../github-repo-publish/SKILL.md) — C7 orchestrator that calls this skill during publish
