---
name: github-code-of-conduct
description: Generates a CODE_OF_CONDUCT.md for a GitHub repository using Contributor Covenant 2.1.
category: GitHub-Community
---

# github-code-of-conduct

**Domain:** `github/community-standards`

Generate a `CODE_OF_CONDUCT.md` for a GitHub repository (Contributor Covenant 2.1).

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/write-code-of-conduct.py` | Write `CODE_OF_CONDUCT.md` to disk |

## Usage

```shell
python3 scripts/write-code-of-conduct.py --email maintainers@example.com --output CODE_OF_CONDUCT.md
```

## Composition by Higher-Level Skills

- `github-repo-templates` (composer) — calls this script for code of conduct
- `github-repo-publish` (orchestrator) — included in template set
