# Git Pre-Execution Safety Stash — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes that auto-load `AGENTS.md` by filename convention.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- Before any multi-commit sequence (atomic-commit batches, history refinement, rebase chains, hunk-staged splits).
- Before any interactive rebase across more than two pick lines against a dirty working tree.
- Whenever the user or a composer skill is about to execute two or more consecutive commits.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full three-phase protocol (Snapshot → Hold → Verify-and-Release), including the new
Phase 1g recovery path for stash-apply failures caused by live editor conflicts. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`git-stash-triage`](../git-stash-triage/SKILL.md) — prerequisite when the stash list is non-empty at Phase 1a
- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md) — primary composer that invokes this
skill before every qualifying sequence
- [`git-commit-edit`](../git-commit-edit/SKILL.md) — invokes this skill before interactive rebase with hunk-splitting
- [`git-history-refinement`](../git-history-refinement/SKILL.md) — invokes this skill before destructive history
rewrites
- [`untracked-scratch-triage`](../untracked-scratch-triage/SKILL.md) — classifies Phase 3a residue
- [`git-ref-content-audit`](../git-ref-content-audit/SKILL.md) — optional Phase 3c.1 per-file blob-equality audit
