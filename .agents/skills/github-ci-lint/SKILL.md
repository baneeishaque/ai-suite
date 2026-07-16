---
name: github-ci-lint
description: Generates CI lint workflows for GitHub Actions by calling markdown lint and python lint base skills.
category: GitHub-Community
---

# github-ci-lint

**Domain:** `github/composer`

C2 composer. Generates CI lint workflows for GitHub Actions by calling
B7 (markdown lint) and B8 (python lint) base skills.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/compose-lint-workflows.py` | Generate lint workflows |

## Called Base Skills

- `github-ci-markdown-lint` (B7)
- `github-ci-python-lint` (B8)

## Composition by Higher-Level Skills

- `github-workflows` (C4) — includes lint workflows
- `github-repo-publish` (C7) — calls during publish

## Related Skills

- [`script-template-extraction`](../script-template-extraction/SKILL.md) — Template Extraction Mandate enforcer; B7 and B8 scripts use `.template` files
- [`skill-cross-reference-audit`](../general/skill-cross-reference-audit/SKILL.md) — automated audit for skill graph issues (duplicates, missing bridges, missing frontmatter)
