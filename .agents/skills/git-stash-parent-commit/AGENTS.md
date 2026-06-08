# Git Stash Parent Commit — Companion Bridge

## Purpose

This file is a bridge for non‑skill‑aware agent runtimes (e.g., Codex CLI, some Cursor profiles) that auto‑load
`AGENTS.md` by filename. The operational single source of truth lives in [`SKILL.md`](SKILL.md). Read that file for the
full procedure, including all mandates, scripts, and verification steps. Do NOT execute any step without first loading
`SKILL.md` — this bridge is intentionally non‑actionable.

## When This Skill Applies

Apply this skill when you need to know the commit that was HEAD at the moment a specific Git stash was created (e.g.,
during stash triage, auditing, or enrichment of stash inspection tables). It is useful whenever a stash reference is
available and you want the parent commit hash and subject line for machine‑ or human‑consumption.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification steps.
Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non‑actionable.

## Cross-References

- [Git Stash Triage Skill](../git-stash-triage/SKILL.md) — consumer that uses this skill to show origin commit for each
stash
- [Git Atomic Commit Construction Skill](../git-atomic-commit-construction/SKILL.md) — references this skill for stash
provenance checks
