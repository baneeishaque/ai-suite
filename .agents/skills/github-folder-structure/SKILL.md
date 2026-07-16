---
name: github-folder-structure
description: Creates the standard repository skeleton with .github/workflows, issue templates, scripts, and docs directories.
category: GitHub-Community
---

# github-folder-structure

**Domain:** `github/community-standards`

Creates the standard repository skeleton: `.github/workflows/`,
`.github/ISSUE_TEMPLATE/`, `scripts/`, `docs/`. Creates `.gitkeep` in each.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/create-folder-structure.py` | Create repo skeleton directories |

## Usage

```shell
python3 scripts/create-folder-structure.py --repo-root /path/to/repo --include-docs
```

## Composition by Higher-Level Skills

- `github-repo-template` (C6) — calls this script for folder structure
- `github-repo-publish` (C7) — calls during publish
