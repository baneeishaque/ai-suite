---
name: github-repo-template
description: Composer that generates the full repository template by combining templates, community docs, structure, and maturity markers.
category: GitHub-Community
---

# github-repo-template

**Domain:** `github/composer`

C6 composer. Generates the full repository template by calling
C1 (templates), C5 (community docs), B18 (structure), and B19 (MaC markers).

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/compose-repo-template.py` | Generate full repo template |

## Called Composers / Base Skills

- `github-repo-templates` (C1) — community standard templates
- `github-docs` (C5) — community documentation
- `github-repo-structure` (B18) — `.github/` directory structure
- `github-maturity-model-maC` (B19) — MaC maturity markers

## Composition by Higher-Level Skills

- `github-repo-publish` (C7) — calls this composer during publish

## Related Skills

- [`script-template-extraction`](../script-template-extraction/SKILL.md) — Template Extraction Mandate enforcer; all C1 and C5 scripts called by this composer use `.template` files via composed base skills
- [`skill-cross-reference-audit`](../general/skill-cross-reference-audit/SKILL.md) — automated audit for skill graph issues (duplicates, missing bridges, missing frontmatter)
