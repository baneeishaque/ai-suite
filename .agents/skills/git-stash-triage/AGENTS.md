# AGENTS.md — git-stash-triage

## Purpose

This file is a bridge for non‑skill‑aware agent runtimes that auto‑load `AGENTS.md` by filename. The operational single
source of truth lives in [`SKILL.md`](SKILL.md). Read that file for the full procedure, including all mandates, scripts,
and verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally
non‑actionable.

## When This Skill Applies

Apply this skill when you need to classify, dispose of, or promote pre‑existing Git stashes to atomic commits or
personal‑sandbox branches — covers hang‑free inspection, content‑based classification, apply‑not‑pop verification, and
rule‑driven disposition.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification steps.
Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non‑actionable.

## Cross-References

- [`git-stash-parent-commit`](../git-stash-parent-commit/SKILL.md) — base skill used to obtain the origin commit for
each stash
- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md) — for commit construction
- [`git-personal-sandbox-remote`](../git-personal-sandbox-remote/SKILL.md) — for Bucket C dispositions
