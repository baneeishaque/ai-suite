---
name: github-security-policy
description: Generates a SECURITY.md for a GitHub repository.
category: GitHub-Community
---

# github-security-policy

**Domain:** `github/community-standards`

Generate a `SECURITY.md` for a GitHub repository.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/write-security-policy.py` | Write `SECURITY.md` to disk |

## Usage

```shell
python3 scripts/write-security-policy.py --email security@example.com --output SECURITY.md
```

## Composition by Higher-Level Skills

- `github-repo-templates` (composer) — calls this script for security policy
- `github-repo-publish` (orchestrator) — included in template set
