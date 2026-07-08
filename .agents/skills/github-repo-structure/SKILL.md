---
name: github-repo-structure
description: Generates the standard .github/ directory structure with issue templates, workflow stubs, and config files.
category: GitHub-Community
---

# github-repo-structure

**Domain:** `github/community-standards`

Generate the standard `.github/` directory structure for a GitHub repository,
including issue templates, workflow stubs, and config files.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/write-repo-structure.py` | Create `.github/` directory layout |

## Usage

```shell
python3 scripts/write-repo-structure.py --output-dir .github
```

## Composition by Higher-Level Skills

- `github-repo-template` (composer) — calls this script for directory structure
- `github-repo-publish` (orchestrator) — included in template set
