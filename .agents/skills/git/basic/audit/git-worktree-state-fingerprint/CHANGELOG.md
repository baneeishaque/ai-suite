# Changelog

| Date | Version | Summary | Rationale |
| :--- | :--- | :--- | :--- |
| 2026-09-27 | v1 | Initial release — `scripts/worktree-state-fingerprint.py` capture/compare primitive (porcelain, index/staged/worktree/untracked sha256, HEAD, commit count). | Extracted as a base primitive: the same byte-level baseline pipeline existed only as prose in `git-commit-edit-in-worktree` Gates 1/8 and hand-rolled in `git-submodule-history-removal` refresh-2. |
