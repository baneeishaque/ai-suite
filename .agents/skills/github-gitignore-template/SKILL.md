---
name: github-gitignore-template
description: Generates a .gitignore file for a GitHub repository scoped by project language such as Python, Node, or generic.
category: GitHub-Community
---

# github-gitignore-template

**Domain:** `github/community-standards`

Generate a `.gitignore` file for a GitHub repository, scoped by project language (Python, Node, generic).

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/write-gitignore-template.py` | Write `.gitignore` to disk |

## Usage

```shell
python3 scripts/write-gitignore-template.py --language python --output .gitignore
```

## Composition by Higher-Level Skills

- `github-repo-templates` (composer) — calls this script for `.gitignore`
- `github-repo-publish` (orchestrator) — included in template set
