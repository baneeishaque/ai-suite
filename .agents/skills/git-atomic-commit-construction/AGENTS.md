# Git Atomic Commit Construction — Companion Bridge

## Purpose

This bridge provides passive context for the `git-atomic-commit-construction` skill, which analyzes working-tree
changes, groups them by logical concern, isolates formatting from semantic edits, performs hunk-based staging, and
proposes an authorization-gated commit sequence.

## When This Skill Applies

It should be invoked whenever the user asks to "commit changes," "stage and commit," "arrange commits," or whenever
working-tree changes span multiple concerns that need atomic grouping.

## Operational Procedure

Read [SKILL.md](SKILL.md) for the full construction, verification, and retirement workflow.
The following contracts locate the relevant guidance for this bridge's readers.

- **Retirement closeout contract**: after commit verification, assess artifact
  completion and references, obtain path-scoped retirement consent, and report
  the disposition of each preview and associated message file. Commit and push
  approval do not grant retirement consent; use recoverable cleanup on macOS.
  The lifecycle skill also governs unfinished parent-plan retention after a
  completed commit batch.

- **Primary Entry Point**: [.agents/skills/git-atomic-commit-construction/SKILL.md](./SKILL.md)

## Cross-References

- **Related Skills**:
    - [`git-commit-edit`](../git-commit-edit/SKILL.md) — for editing commits already in history
    - [`git-history-refinement`](../git-history-refinement/SKILL.md) — for reconstructing diverged history
