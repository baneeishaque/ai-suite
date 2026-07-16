# GitHub Repo Templates — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to generate all community standard templates at once (gitignore, code of conduct, contributing, security, support, README, issue/PR templates).
- A higher-level orchestrator requires the full template set.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including script invocation with `--owner`, `--repo-name`, and `--output-dir`. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`github-repo-template`](../github-repo-template/SKILL.md) — C6 composer that calls this skill
- [`github-repo-publish`](../github-repo-publish/SKILL.md) — C7 orchestrator
