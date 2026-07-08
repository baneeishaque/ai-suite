---
name: github-repo-templates
description: Composer that calls base skills to generate the full set of community standard templates for a GitHub repository.
category: GitHub-Community
---

# github-repo-templates

**Domain:** `github/composer`

C1 composer. Calls base skills B1-B6, B12-B17 to generate the full set of
community standard templates for a GitHub repository.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/compose-templates.py` | Generate all templates |

## Called Base Skills

- `github-gitignore-template` (B12)
- `github-code-of-conduct` (B13)
- `github-contributing-guide` (B14)
- `github-security-policy` (B15)
- `github-support-docs` (B16)
- `github-readme-template` (B17)
- `github-issue-template-bug` (B3)
- `github-issue-template-feature` (B4)
- `github-issue-template-documentation` (B5)
- `github-pr-template` (B6)

## Composition by Higher-Level Skills

- `github-repo-template` (C6) — calls this composer for template set
- `github-repo-publish` (C7) — calls this composer during publish

## Related Skills

- [`script-template-extraction`](../script-template-extraction/SKILL.md) — Template Extraction Mandate enforcer; all base-template skills called by this composer use `.template` files extracted by its automation
- [`skill-cross-reference-audit`](../general/skill-cross-reference-audit/SKILL.md) — automated audit for skill graph issues (duplicates, missing bridges, missing frontmatter)
