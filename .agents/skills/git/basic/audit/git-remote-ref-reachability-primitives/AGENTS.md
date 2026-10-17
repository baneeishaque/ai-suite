# Git Remote Ref Reachability Primitives — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational
SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to prove whether a commit already exists on any remote, rather than assuming
  from local state.
- You need to know how far a branch's local-only commit chain extends before doing
  anything destructive to it.
- You need a live yes/no answer on whether a remote branch exists, for example after a
  push or a delete.

To learn what naming or grouping scheme a remote follows, use
[`git-remote-branch-convention-discovery`](../../../config/git-remote-branch-convention-discovery/SKILL.md)
instead — that is a separate question with a separate consumer.

Everything here is read-only. To push, rename, or delete a remote branch, use
[`git-remote-branch-lifecycle`](../../../repo/git-remote-branch-lifecycle/SKILL.md)
instead.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all three
script contracts, exit codes, and the cached-ref caveats. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the script contracts and safety rules.
- [`git-remote-branch-convention-discovery`](../../../config/git-remote-branch-convention-discovery/SKILL.md)
  — sibling read-only base owning convention inference, split per decision D1=C.
- [`git-remote-branch-lifecycle`](../../../repo/git-remote-branch-lifecycle/SKILL.md) —
  the mutating composer that consumes these primitives.
- [`git-repository-status`](../../../../git-repository-status/SKILL.md) — sibling
  read-only status surface.
