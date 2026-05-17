# AGENTS.md — git-pre-execution-safety-stash

This directory hosts the **Git Pre-Execution Safety Stash** skill.

| Field | Value |
|---|---|
| Skill ID | `git-pre-execution-safety-stash` |
| Active SSOT | [SKILL.md](SKILL.md) |
| Category | Git & Repository Management |
| Composers | `git-atomic-commit-construction`, `git-history-refinement`, `git-rebase-standardization`, `git-commit-edit` |
| Siblings | `git-stash-triage`, `untracked-scratch-triage` |

When the user (or a composer skill) is about to execute any sequence of
two or more commits — atomic-commit batches, history-refinement runs,
rebase chains, hunk-staged splits — invoke the SKILL.md protocol to
capture an apply-not-pop working-tree snapshot, hold it across the
sequence, and verify-then-drop only at end-of-session.

See [SKILL.md](SKILL.md) for the full three-phase protocol.
