# Git Remote Branch Lifecycle — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational
SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are pushing a local branch to a remote for the first time and need the push proven,
  not assumed.
- A remote branch name does not match the grouping scheme that remote already follows and
  the user wants it corrected.
- You are about to delete a remote branch and need the deletion verified and gated.
- You need to decide whether to set upstream tracking now or offer it as a follow-up.

For read-only questions — is this commit on a remote, how far back does the remote already
hold content — use
[`git-remote-ref-reachability-primitives`](../../basic/audit/git-remote-ref-reachability-primitives/SKILL.md)
instead. This skill mutates.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the authorization
gates, the rename guardrails, and the script invocations. Do NOT execute any step without
first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the phase order, gates, and guardrails.
- [`git-remote-ref-reachability-primitives`](../../basic/audit/git-remote-ref-reachability-primitives/SKILL.md)
  — the read-only base this skill sequences.
- [`git-personal-sandbox-remote`](../../../git-personal-sandbox-remote/SKILL.md) — owns the
  `personal/` grouping convention.
