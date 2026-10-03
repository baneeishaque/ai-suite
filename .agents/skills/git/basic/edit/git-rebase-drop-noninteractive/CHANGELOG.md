# Changelog

| Date | Version | Summary | Rationale |
| :--- | :--- | :--- | :--- |
| 2026-08-14 | v1 | Initial release — scripted non-interactive rebase-todo rewrite (pick → drop/edit). | Created from the documented anthropics_skills production workflow; base primitive for `git-commit-edit-in-worktree`. |
| 2026-09-27 | v1.0.1 | Fixed `write-drop-todo.py`: NameError crash (`not_SHA_RE`); `--edit` now wins over the positional drop set; SHA matching is prefix-tolerant (full vs abbreviated) with an ambiguity guard; todo-path positional is order-tolerant (first for direct calls, last as git appends it via `GIT_SEQUENCE_EDITOR`). | Composer callers pass `sha --edit sha` with full SHAs against abbreviated todo files and git appends the todo path last — the documented contract was unusable end-to-end. |
