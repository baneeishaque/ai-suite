# VS Code state.vscdb Merge — Companion Bridge

## Purpose

This file is a bridge for non-skill-aware agent runtimes that auto-load `AGENTS.md` by filename convention. The operational single source of truth lives in [`SKILL.md`](SKILL.md). Read that file for the full procedure, including all mandates, scripts, and verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## When This Skill Applies

Apply this skill when a VS Code `state.vscdb` SQLite database differs between two Git refs (stash vs HEAD, commit vs commit, branch vs branch). The skill extracts both versions, reads their `ItemTable` key-value pairs, and reports stash-only / HEAD-only / common-modified keys. A `--merge` flag creates a merged database copying stash-only keys into HEAD's copy, but only after explicit user authorization.

Common scenarios:
- Stash triage: a `state.vscdb` file differs between stash@{N} and HEAD
- VS Code state audit: comparing settings/state across branches or commits
- Environment setup: extracting keys from a reference environment

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full step-by-step procedure, including script invocation, report interpretation, and the merge authorization gate. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`git-stash-triage`](../git-stash-triage/SKILL.md) — composer skill that invokes this base skill during Phase 4d (Selective File Restoration) for per-file analysis of `state.vscdb` files
- [`git-ref-content-audit`](../git-ref-content-audit/SKILL.md) — bulk blob-equality audit between two refs; complements this skill's key-level analysis
