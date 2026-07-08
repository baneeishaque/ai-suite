---
name: github-readme-template
description: Generates a README.md template for a GitHub repository.
category: GitHub-Community
---

# github-readme-template

**Domain:** `github/community-standards`

Generate a `README.md` template for a GitHub repository.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/write-readme-template.py` | Write `README.md` to disk |

## Usage

```shell
python3 scripts/write-readme-template.py --repo-name myrepo --description "My project" --output README.md
```

## Composition by Higher-Level Skills

- `github-repo-templates` (composer) — calls this script for README
- `github-repo-publish` (orchestrator) — included in template set
