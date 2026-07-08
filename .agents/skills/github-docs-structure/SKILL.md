---
name: github-docs-structure
description: Creates the standard docs/ directory tree with architecture, decisions, implementation-plans, and guides subdirectories.
category: GitHub-Community
---

# github-docs-structure

**Domain:** `github/community-standards`

Creates the standard `docs/` directory tree: `docs/architecture/`,
`docs/decisions/`, `docs/implementation-plans/`, `docs/guides/`.
Creates `.gitkeep` in each leaf directory.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/create-docs-structure.py` | Create `docs/` directory structure |

## Usage

```shell
python3 scripts/create-docs-structure.py --repo-root /path/to/repo
```

## Composition by Higher-Level Skills

- `github-docs` (C5) — calls this script for docs structure
- `github-repo-template` (C6) — included in template set
- `github-repo-publish` (C7) — calls during publish
