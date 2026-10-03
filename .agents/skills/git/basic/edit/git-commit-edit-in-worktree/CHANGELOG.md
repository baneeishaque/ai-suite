# Changelog

| Date | Version | Summary | Rationale |
| :--- | :--- | :--- | :--- |
| 2026-09-27 | v2.0.0 | Modes (A scratch-worktree / B dedicated-worktree in-place), gate delegation to `git-worktree-state-fingerprint` (Gates 1/8) and `git-commit-replace-and-replay` (Mode B prepare/finish/verify), range-diff parity at Gate 7, `plan-commit-edit.py --mode`, `-d`→`-D` and no-upstream push nuances. | Codifies the in-place route (Mode B) and scripts the previously prose-only baseline gates; writer dependency now functional (base v1.0.1). |
| 2026-08-14 | v1 | Initial release — worktree-isolated any-commit edit (drop / amend / reword / edit) with baseline gate, scripted rebase via `git-rebase-drop-noninteractive`, `reset --soft` fast-forward, and content-level (byte/index) verification. | Created from the documented anthropics_skills production workflow; the refresh-2 baseline gate was strengthened at authoring. |
