# Traceability

| Date | Relationship |
| :--- | :--- |
| 2026-09-27 | v2.0.0 adds Mode B (dedicated-worktree in-place, delegating to `git-commit-replace-and-replay`) and scripts Gates 1/8 via `git-worktree-state-fingerprint`; codifies the proven in-place route (a commit-edit round-trip on a dedicated linked worktree with dirty gitlink state surviving `--autostash`). |
| 2026-08-14 | v1 — the composer protocol (baseline / plan / safety / isolate / amend / recovery / tree-check / fast-forward / cleanup gates); includes the `reset --soft` fast-forward and byte-level baseline comparison. |
