---
name: Git Commit Preview Verify
description: Passive context bridge for verifying commit preview execution status.
category: Git & Repository Management
---

# Git Commit Preview Verify (Ref)

This bridge provides passive context for the `git-commit-preview-verify`
skill, which parses commit-preview markdown files and verifies whether
the listed commits have been executed against git history.

It should be invoked whenever the user asks to check whether planned
commits were completed, or points to an existing preview file for
verification.

- **Primary Entry Point**:
  [.agents/skills/git/basic/edit/git-commit-preview-verify/SKILL.md](./SKILL.md)
- **Related Skills**:
    - [`git-atomic-commit-construction`](../../../../git-atomic-commit-construction/SKILL.md)
      — composer that generates previews
    - [`git-commit-metadata-extraction`](../../../../git-commit-metadata-extraction/SKILL.md)
      — for individual commit metadata
