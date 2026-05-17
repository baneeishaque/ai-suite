# AGENTS.md — git-dependent-branch-restack-cascade

This is the companion bridge for the
[`git-dependent-branch-restack-cascade`](SKILL.md) skill.

## Purpose

After a base branch tip advances (via decommission cherry-pick, branch
promotion, or any other fast-forward update), every other branch still
rooted on the **old** tip must be rebased onto the **new** tip. This skill
discovers those dependents and cascades the restack with per-dependent
patch-id parity verification and per-push authorization gating.

## When to consult `SKILL.md`

- After completing [`git-parallel-branch-decommission`](../git-parallel-branch-decommission/SKILL.md)
  Phase 4 (the canonical branch just moved).
- After completing [`git-branch-promotion`](../git-branch-promotion/SKILL.md)
  (the canonical / team branch just moved).
- After any manual cherry-pick / amend / rebase that advances a base branch
  on which other branches are stacked.

## Relationship to siblings

- [`git-personal-sandbox-restack`](../git-personal-sandbox-restack/SKILL.md)
  — the single-dependent ancestor. This skill generalizes it to N
  dependents and removes the personal-sandbox specialization.
- [`git-rebase-standardization`](../git-rebase-standardization/SKILL.md)
  — the underlying rebase-mechanics owner.
- [`git-divergence-audit`](../git-divergence-audit/SKILL.md) — the
  dependent-discovery primitive.

## Active SSOT

All operational logic lives in [`SKILL.md`](SKILL.md). This file is a
passive pointer.
