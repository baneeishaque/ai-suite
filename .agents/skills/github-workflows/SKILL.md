---
name: github-workflows
description: Composer that generates all GitHub Actions workflows by assembling base skills into the full .github/workflows/ directory.
category: GitHub-Community
---

# github-workflows

**Domain:** `github/composer`

C4 composer. Generates all GitHub Actions workflows by calling B7-B11
base skills to assemble the full `.github/workflows/` directory.

## Scripts

| Script                            | Purpose                |
|------------------------------------|------------------------|
| `scripts/compose-workflows.py` | Generate all workflows |

## Called Base Skills

- `github-ci-markdown-lint` (B7)
- `github-ci-python-lint` (B8)
- `github-pr-labeler` (B11)
- `github-sync-description` (B9)
- `github-sync-topics` (B10)

## Composition by Higher-Level Skills

- `github-repo-publish` (C7) — calls during publish

## Related Skills

- [`script-template-extraction`](../script-template-extraction/SKILL.md) — Template Extraction Mandate enforcer; all B7-B11 scripts called by this composer use `.template` files
- [`skill-cross-reference-audit`](../general/skill-cross-reference-audit/SKILL.md) — automated audit for skill graph issues (duplicates, missing bridges, missing frontmatter)
