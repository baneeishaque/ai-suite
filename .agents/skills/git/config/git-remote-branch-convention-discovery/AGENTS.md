# Git Remote Branch Convention Discovery — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational
SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are about to push a branch to a remote whose naming or grouping scheme you have not
  confirmed, and you want the remote to tell you its own convention instead of assuming.
- A remote branch name was flagged as inconsistent with the rest of that remote.
- You need to know which existing branch names break the remote's dominant convention.

For questions about whether a commit or ref EXISTS on a remote, use
[`git-remote-ref-reachability-primitives`](../../basic/audit/git-remote-ref-reachability-primitives/SKILL.md)
instead. This skill only reads the remote's naming organization.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the JSON field
contract, the `dominant_prefix: null` case, and the hint-versus-decision boundary. Do NOT
execute any step without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the inference contract.
- [`git-remote-branch-lifecycle`](../../repo/git-remote-branch-lifecycle/SKILL.md) — the
  mutating composer that consumes this primitive.
- [`git-remote-ref-reachability-primitives`](../../basic/audit/git-remote-ref-reachability-primitives/SKILL.md)
  — sibling read-only base for reachability.
