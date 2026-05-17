# Git Drop Commit With Divergent Recreation — AGENTS Bridge

Active SSOT: [SKILL.md](./SKILL.md)

## When this skill applies

- User asks to drop a commit and the commit deletes one or more files.
- A later commit on the same branch re-creates at least one of those files.
- Inspection shows the pre-deletion blob and the recreated blob have diverged
  (each carries unique content the other lacks).

## When to defer

- Blobs are byte-identical → use [`git-commit-edit`](../git-commit-edit/SKILL.md)
  with `drop` action directly.
- One blob is a strict superset of the other → use `git-commit-edit drop` and
  resolve the conflict with the superset side; no full composer needed.

See [SKILL.md](./SKILL.md) for the full nine-step protocol.
