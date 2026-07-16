---
name: Git Commit Message Delivery
description: Passive context bridge for the git-commit-message-delivery base primitive.
category: Git & Repository Management
---

# Git Commit Message Delivery (Ref)

Base primitive that documents how to safely pass multi-line commit messages to
`git commit` without shell-escaping failures, and how to reliably verify commit
contents using `--name-only` instead of `--stat`.

- **Primary Entry Point**: [.agents/skills/git-commit-message-delivery/SKILL.md](./SKILL.md)
- **Related Skills**:
    - [`../git-atomic-commit-construction/SKILL.md`](../git-atomic-commit-construction/SKILL.md) — primary consumer
    - [`../git-commit-message-reword/SKILL.md`](../git-commit-message-reword/SKILL.md) — GIT_EDITOR pattern consumer
