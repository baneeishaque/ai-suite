# Claude Config Change Gate — Companion Bridge

## Purpose

This file is the companion bridge for the
[`claude-config-change-gate`](SKILL.md) domain composer skill.
It exists so non-skill-aware agent runtimes discover this skill exists.
The operational Single Source of Truth lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Apply when a repository contains claude auto-timestamped configuration
files (`claude/.last-cleanup`, `claude/plugins/known_marketplaces.json`)
and you want to gate git operations so that commits with only timestamp
changes are blocked. The skill composes the JSON content comparison base
primitive (Layer 0) with the git operation blocking hooks mechanism
(Layer 2) for this specific domain.

Do NOT apply when the blocking mechanism is needed without claude config
awareness (use `git-operation-blocking-hooks` instead) or when only JSON
comparison is needed (use `json-content-compare-ignore-keys` directly).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [SKILL.md](SKILL.md) — the SSOT
- [`json-content-compare-ignore-keys`](../json-content-compare-ignore-keys/SKILL.md) — composed base primitive (Layer 0)
- [`git-operation-blocking-hooks`](../git-operation-blocking-hooks/SKILL.md) — composed mechanism composer (Layer 2)
- [`git-global-hook-bootstrap`](../git-global-hook-bootstrap/SKILL.md) — upstream Layer-1 skill (part of the composed mechanism)
- [`git-repo-hook-chain`](../git-repo-hook-chain/SKILL.md) — upstream Layer-1 skill (part of the composed mechanism)
- [`git-alias-preflight`](../git-alias-preflight/SKILL.md) — upstream Layer-1 skill (part of the composed mechanism)
