---
name: github-maturity-model-maC
description: Adds Model as Code maturity markers with shield.io badges wrapped in HTML comment markers to a GitHub repository's README.
category: GitHub-Community
---

# github-maturity-model-maC

**Domain:** `github/community-standards`

Add Model as Code (MaC) maturity markers to a GitHub repository's README,
using shield.io badges wrapped in MaC HTML comment markers.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/write-maturity-markers.py` | Write MaC maturity markers |

## Usage

```shell
python3 scripts/write-maturity-markers.py --maturity stable --output README.md
```

## Composition by Higher-Level Skills

- `github-repo-template` (composer) — calls this script for MaC markers
- `github-repo-publish` (orchestrator) — included in template set
