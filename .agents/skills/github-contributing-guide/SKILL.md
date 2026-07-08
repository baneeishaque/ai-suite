---
name: github-contributing-guide
description: Generates a CONTRIBUTING.md for a GitHub repository.
category: GitHub-Community
---

# github-contributing-guide

**Domain:** `github/community-standards`

Generate a `CONTRIBUTING.md` for a GitHub repository.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/write-contributing-guide.py` | Write `CONTRIBUTING.md` to disk |

## Usage

```shell
python3 scripts/write-contributing-guide.py --owner myorg --repo-name myrepo --output CONTRIBUTING.md
```

## Composition by Higher-Level Skills

- `github-repo-templates` (composer) — calls this script for contributing guide
- `github-repo-publish` (orchestrator) — included in template set
