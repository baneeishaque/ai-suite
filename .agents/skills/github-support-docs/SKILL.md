---
name: github-support-docs
description: Generates a SUPPORT.md for a GitHub repository.
category: GitHub-Community
---

# github-support-docs

**Domain:** `github/community-standards`

Generate a `SUPPORT.md` for a GitHub repository.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/write-support-docs.py` | Write `SUPPORT.md` to disk |

## Usage

```shell
python3 scripts/write-support-docs.py --owner myorg --repo-name myrepo --output SUPPORT.md
```

## Composition by Higher-Level Skills

- `github-repo-templates` (composer) — calls this script for support docs
- `github-repo-publish` (orchestrator) — included in template set
