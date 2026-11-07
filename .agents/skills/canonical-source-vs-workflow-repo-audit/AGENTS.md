# Canonical Source vs Workflow Repo Audit — Companion Bridge

## Purpose

Expose the repository-role classifier to non-skill-aware runtimes.
The operational SSOT lives in [SKILL.md](SKILL.md).

## When This Skill Applies

- Before editing unfamiliar source whose repository role is unclear.
- When similarly named repositories separate canonical source from workflow or backup responsibilities.
- When a file path must identify the enclosing Git repository for the role audit.

## Operational Procedure

Read [SKILL.md](SKILL.md) for existing-file/directory inputs, invalid-path
handling, scoring, output contracts, recovery guidance, and regression checks.
The classifier reports evidence; the caller decides whether an edit belongs there.

## Cross-References

- [Atomic commit construction](../git-atomic-commit-construction/SKILL.md) — pre-edit classification consumer.
- [Personal sandbox remote](../git-personal-sandbox-remote/SKILL.md) — placement of personal-only work.
