---
name: github-sync
description: Composer that generates GitHub metadata sync workflows by calling sync description and sync topics base skills.
category: GitHub-Community
---

# github-sync

**Domain:** `github/composer`

C3 composer. Generates GitHub metadata sync workflows by calling
B9 (sync description) and B10 (sync topics) base skills.

## Scripts

| Script                              | Purpose                |
|--------------------------------------|------------------------|
| `scripts/compose-sync-workflows.py` | Generate sync workflows |

## Called Base Skills

- `github-sync-description` (B9)
- `github-sync-topics` (B10)

## Composition by Higher-Level Skills

- `github-workflows` (C4) — includes sync workflows
- `github-repo-publish` (C7) — calls during publish

## Related Skills

- [`script-template-extraction`](../script-template-extraction/SKILL.md) — Template Extraction Mandate enforcer; B9 and B10 scripts use `.template` files
- [`skill-cross-reference-audit`](../general/skill-cross-reference-audit/SKILL.md) — automated audit for skill graph issues (duplicates, missing bridges, missing frontmatter)
