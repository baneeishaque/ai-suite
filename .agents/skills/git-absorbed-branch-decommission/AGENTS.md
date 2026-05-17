# AGENTS.md — git-absorbed-branch-decommission

This is the companion bridge for the
[`git-absorbed-branch-decommission`](SKILL.md) skill.

## Purpose

Safely delete a stale branch whose content has been fully absorbed by a
sibling / successor branch — either by direct ancestor containment
(trivial) or by patch-id equivalence after a re-cherry-pick / rollback
workflow (forensic). Includes the mandatory tip-file-set parity check
that catches files which exist on the stale branch but are missing on
the live branch.

## When to consult `SKILL.md`

- A personal-named branch lingers on a team repo and the integration
  team claims its content is "already on `<live>`".
- A `_via_rollback` / `_new` / `_v2` style replacement branch has
  superseded an older sibling and the older one is now stale.
- Cleanup of an old release / experiment branch after the integration
  line moved.

## Relationship to siblings

- [`git-parallel-branch-decommission`](../git-parallel-branch-decommission/SKILL.md)
  — use that when the stale branch has UNIQUE content that must be
  preserved via fan-out. Use THIS skill when the content is already
  absorbed.
- [`git-branch-promotion`](../git-branch-promotion/SKILL.md) — use that
  to MOVE a refined branch onto canonical. Use THIS skill to DELETE a
  stale branch after promotion has already happened elsewhere.
- [`git-divergence-audit`](../git-divergence-audit/SKILL.md) — the
  read-only primitive; use directly when no deletion is intended.

## Active SSOT

All operational logic lives in [`SKILL.md`](SKILL.md). This file is a
passive pointer.
