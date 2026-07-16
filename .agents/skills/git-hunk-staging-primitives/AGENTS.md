# Git Hunk Staging Primitives — Companion Bridge

## Purpose

This file is the passive bridge for non-skill-aware agent runtimes.
The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- Any workflow needing to stage file content via
  `git update-index --cacheinfo` or `git apply --cached` without
  modifying the working tree.
- Commit construction, history refinement, patch manipulation,
  submodule sync.
- When `git add -p` hunk splitting fails and programmatic fallback
  is needed.
- AGENTS.md table row registration (interleaving mandate or
  skill-factory).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure,
including all mandates, script invocations, and verification steps.
Do NOT execute any step without first loading `SKILL.md` — this
bridge is intentionally non-actionable.

## Cross-References

- `git-atomic-commit-construction` — Composer orchestrating these
  primitives.
- `git-history-refinement` — Composer using primitives for commit
  splitting.
- `git-pre-execution-safety-stash` — Uses staging for safety
  snapshots.
- `script-over-instruction-decomposition` — Mandates Tier-A
  extraction for all primitives.
