# Untracked Scratch Triage — Agents Bridge

This directory contains the `untracked-scratch-triage` skill.

The active, authoritative instructions live in [SKILL.md](SKILL.md).
This file exists only to provide passive context for agents that
auto-discover `AGENTS.md` files.

## When to Read SKILL.md

Read [SKILL.md](SKILL.md) when:

- After a commit, `git status` still lists untracked files whose origin
  is unclear.
- The user asks "what about the leftover files?".
- Bulk untracked artifacts appear (`*.log`, `*.tmp`, `.gh_*`,
  `nohup.out`, `core.*`).
- A file's content looks like it belongs to a *different* repository's
  session.

For broader / different scopes, see the
[Related Skills](SKILL.md#related-skills) section in `SKILL.md`.
