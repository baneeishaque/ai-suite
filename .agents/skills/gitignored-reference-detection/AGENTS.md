# Gitignored Reference Detection — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- A committed markdown file links to a local path that is gitignored and will not survive a standalone clone.
- An AI tool reports a broken reference to a file inside `.claude/skills/` or another gitignored directory.
- You are auditing a skill before publication and want to verify every cross-reference resolves.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full detection and remediation workflow, including git check-ignore usage, public URL discovery, and verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`detect-gitignored-refs.py`](scripts/detect-gitignored-refs.py) — automated scanner
- [`gitignore-rules`](../gitignore-rules/SKILL.md) — authoring `.gitignore` rules
- [`redaction-portability`](../redaction-portability/SKILL.md) — broader portability standards
- [`mrt-configuration-debug`](../mrt-configuration-debug/SKILL.md) — concrete application example
