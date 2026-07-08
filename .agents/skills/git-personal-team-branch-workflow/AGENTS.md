# Git Personal Team Branch Workflow — Companion Bridge

## Purpose

This file is the passive context bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You have a dual-remote setup (`origin` + `personal`) and a
  `personal/<purpose>` branch that is a superset of the team branch.
- You are actively working on team tickets and committing to the team branch.
- You need to keep personal commits always at the tip of `personal/<purpose>` —
  immediately restacking after each team commit.
- At session end, you push both branches to their respective remotes.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
session workflow (start → team work cycle → session end), the companion script,
and all failure-mode resolutions. Do NOT execute any step without first loading
`SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`git-personal-sandbox-remote`](../git-personal-sandbox-remote/SKILL.md) —
  prerequisite: dual-remote setup and personal branch creation
- [`git-personal-sandbox-restack`](../git-personal-sandbox-restack/SKILL.md) —
  deep restack verification via six-axis equality audit
- [`git-personal-content-extraction`](../git-personal-content-extraction/SKILL.md)
  — reactive sibling skill for extracting personal commits from a mixed branch
- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  — atomic commit discipline on the team branch
