# Git Operation Blocking Hooks — Companion Bridge

## Purpose

This file is the companion bridge for the
[`git-operation-blocking-hooks`](SKILL.md) mechanism composer skill.
It exists so non-skill-aware agent runtimes discover this skill exists.
The operational Single Source of Truth lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Apply when setting up a complete git operation blocking gate that
integrates global hook bootstrap (`~/.git-hooks/`), repo-level hooks
(`core.hooksPath`, `lib.bash` dispatch), and pre-flight aliases (`git
status` → check + real status) into a single workflow. This is a
prose-only composer — the actual scripts live in the three general
infrastructure skills it composes.

Do NOT apply when only one piece is needed (e.g., just repo hooks
without the global bootstrap). In that case, use the individual
Layer-1 skill directly.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, the End-to-End Bootstrap Chain diagram, and verification
steps. Do NOT execute any step without first loading `SKILL.md` — this
bridge is intentionally non-actionable.

## Cross-References

- [SKILL.md](SKILL.md) — the SSOT
- [`git-global-hook-bootstrap`](../git-global-hook-bootstrap/SKILL.md) — composed Layer-1 skill: machine hook setup
- [`git-repo-hook-chain`](../git-repo-hook-chain/SKILL.md) — composed Layer-1 skill: repo hook chain
- [`git-alias-preflight`](../git-alias-preflight/SKILL.md) — composed Layer-1 skill: alias registration
- [`claude-config-change-gate`](../claude-config-change-gate/SKILL.md) — domain composer that consumes this mechanism
