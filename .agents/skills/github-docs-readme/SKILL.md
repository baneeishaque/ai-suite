---
name: github-docs-readme
description: Provides a docs/README.md with standard documentation structure sections.
category: GitHub-Community
---

# github-docs-readme

**Domain:** `github/community-standards`

Provides a `docs/README.md` with standard documentation structure sections.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/write-docs-readme.py` | Write `docs/README.md` |

## Usage

```shell
python3 scripts/write-docs-readme.py --project-name myproject --output docs/README.md
```

## Composition by Higher-Level Skills

- `github-docs` (C5) — calls this script for docs README
- `github-repo-template` (C6) — included in template set
- `github-repo-publish` (C7) — calls during publish
