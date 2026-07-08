---
name: github-repo-publish
description: Top-level orchestrator that creates a GitHub repository with full community standards including templates, workflows, and docs.
category: GitHub-Community
---

# github-repo-publish

**Domain:** `github/orchestrator`

C7 top-level orchestrator. Creates a GitHub repository with full community
standards: issue/PR templates, CI lint workflows, sync workflows, PR labeler,
code of conduct, contributing guide, security policy, support docs, README,
.gitignore, MaC maturity markers.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/publish-repo.py` | Publish repo with all community standards |

## Called Composers / Base Skills

- `gh-repo-create` (B1) — create the repository
- `gh-repo-edit-metadata` (B2) — set description and topics
- `github-repo-template` (C6) — generate full template set
- `github-workflows` (C4) — generate CI and sync workflows

## Orchestration Flow

1. Create repository (B1)
2. Set description and topics (B2)
3. Clone the new repository
4. Generate all community standards templates (C6)
5. Generate all GitHub Actions workflows (C4)
6. Commit and push

## Related Skills

- [`script-template-extraction`](../script-template-extraction/SKILL.md) — Template Extraction Mandate enforcer; all template content written by C6 and C4 scripts uses `.template` files
- [`skill-cross-reference-audit`](../general/skill-cross-reference-audit/SKILL.md) — automated audit for skill graph issues (duplicates, missing bridges, missing frontmatter)
