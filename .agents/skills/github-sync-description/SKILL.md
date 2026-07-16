---
name: github-sync-description
description: Base skill — write a GitHub Actions workflow that syncs a repository description from a MaC (Markdown-as-Configuration) marker block in README.md. Uses `<!-- START_DESCRIPTION -->` / `<!-- END_DESCRIPTION -->` HTML comment markers for parsing.
category: CI/CD & DevOps
layer: Base
script: scripts/write-description-sync-workflow.py
---

# GitHub Sync Description Skill (v1)

> **Skill ID:** `github-sync-description`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)
> **Layer:** Base

## 1. When to Apply

Use this skill whenever an agent must **create or update** a GitHub Actions workflow that synchronizes a repository's description from a Markdown-as-Configuration (MaC) marker block in `README.md`.

**Triggers:**

- "Sync repo description from README."
- "Keep repo description in sync with README content."
- "Create a workflow that reads description from README and updates the repo."

**Anti-trigger:** If topics also need syncing, use [`github-sync-topics`](../github-sync-topics/SKILL.md). For a combined sync, a higher-level `github-sync` composer should aggregate both.

## 2. MaC Marker Parsing Pattern

The workflow extracts the description from `README.md` using HTML comment markers:

```markdown
<!-- START_DESCRIPTION -->
Your repository description here (plain text, single line after processing)
<!-- END_DESCRIPTION -->
```

The embedded Python script:

1. Searches for the `<!-- START_DESCRIPTION -->` / `<!-- END_DESCRIPTION -->` markers
2. Extracts text between them, strips whitespace, collapses internal whitespace
3. Exits with code 1 if markers are not found (preventing silent description wipe)

## 3. Environment & Dependencies

| Tool | Purpose | Verification |
|---|---|---|
| `python3` (3.10+) | Script engine | `python3 --version` |

The generated workflow requires `gh` CLI (authenticated via `GITHUB_TOKEN`) and Python 3 on the runner.

## 4. Operational Logic

### 4.1 Script Catalogue

| Script | Purpose | Required Args |
|---|---|---|
| [`scripts/write-description-sync-workflow.py`](scripts/write-description-sync-workflow.py) | Write `.github/workflows/sync-description.yml` | None (all optional with defaults) |

### 4.2 Invocation

```bash
python3 .agents/skills/github-sync-description/scripts/write-description-sync-workflow.py \
    --repo-root /path/to/repo
```

**Arguments:**

| Flag | Default | Purpose |
|---|---|---|
| `--repo-root` | `.` | Root of the target repository |

### 4.3 YAML Output

The script produces `.github/workflows/sync-description.yml`:

```yaml
name: Sync Description

on:
  push:
    branches: [main, master]
    paths: ['README.md']

jobs:
  sync:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - name: Extract description
        id: extract
        run: |
          DESCRIPTION=$(python3 -c "
import re, sys
text = open('README.md').read()
m = re.search(r'<!-- START_DESCRIPTION -->(.*?)<!-- END_DESCRIPTION -->', text, re.DOTALL)
if m:
    desc = m.group(1).strip()
    desc = re.sub(r'\s+', ' ', desc)
    print(desc, end='')
else:
    sys.exit(1)
")
          echo "description=$DESCRIPTION" >> $GITHUB_OUTPUT
      - name: Update repo description
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh repo edit ${{ github.repository }} --description "${{ steps.extract.outputs.description }}"
```

### 4.4 Exit Codes

| Code | Meaning |
|---|---|
| `0` | Workflow written successfully |
| `1` | Write error (permissions, invalid path) |

## 5. Composition by Higher-Level Skills

| Composer | Purpose |
|----------|---------|
| [`github-sync`](../github-sync/SKILL.md) | C3 — calls this skill for sync workflow orchestration |
| [`github-workflows`](../github-workflows/SKILL.md) | C4 — calls this skill for full workflow assembly |
| [`github-repo-publish`](../github-repo-publish/SKILL.md) | C7 — calls this skill during publish orchestration |

## 6. Related Skills

- [`github-sync-topics`](../github-sync-topics/SKILL.md) — companion base skill for topic sync
- [`gh-repo-edit-metadata`](../gh-repo-edit-metadata/SKILL.md) — direct metadata editing via `gh`
