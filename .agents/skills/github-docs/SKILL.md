---
name: github-docs
description: Composer that generates GitHub community documentation files including code of conduct, contributing guide, security policy, and support docs.
category: GitHub-Community
---

# github-docs

**Domain:** `github/composer`

C5 composer. Generates GitHub community documentation files (code of conduct,
contributing guide, security policy, support docs) by calling B13-B16.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/compose-community-docs.py` | Generate community docs |

## Called Base Skills

- `github-code-of-conduct` (B13)
- `github-contributing-guide` (B14)
- `github-security-policy` (B15)
- `github-support-docs` (B16)

## Composition by Higher-Level Skills

- `github-repo-template` (C6) — includes these docs
- `github-repo-publish` (C7) — calls during publish

## Related Skills

- [`script-template-extraction`](../script-template-extraction/SKILL.md) — Template Extraction Mandate enforcer; B13-B16 scripts use `.template` files
- [`skill-cross-reference-audit`](../general/skill-cross-reference-audit/SKILL.md) — automated audit for skill graph issues (duplicates, missing bridges, missing frontmatter)
