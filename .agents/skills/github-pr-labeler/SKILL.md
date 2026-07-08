---
name: github-pr-labeler
description: Base skill — write a GitHub Actions PR labeler workflow AND its companion labeler-config.yml. The two files are coupled because the workflow references the config via `configuration-path`.
category: CI/CD & DevOps
layer: Base
script: scripts/write-pr-labeler.py
---

# GitHub PR Labeler Skill (v1)

> **Skill ID:** `github-pr-labeler`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)
> **Layer:** Base

## 1. When to Apply

Use this skill whenever an agent must **set up automatic PR labeling** based on changed file paths. The script writes two coupled files:

| File | Purpose |
|---|---|
| `.github/workflows/pr-labeler.yml` | GitHub Actions workflow that triggers on PR events |
| `.github/labeler-config.yml` | Label mapping rules consumed by `actions/labeler@v5` |

These two files are **coupled**: the workflow references the config via `configuration-path: .github/labeler-config.yml`. Both must exist for the labeler to function.

**Triggers:**

- "Add automatic PR labeling."
- "Set up PR labeler for changed files."
- "Configure PR labels based on file paths."

## 2. Environment & Dependencies

| Tool | Purpose | Verification |
|---|---|---|
| `python3` (3.10+) | Script engine | `python3 --version` |

The generated workflow uses `actions/labeler@v5` (publicly available on the GitHub marketplace).

## 3. Operational Logic

### 3.1 Script Catalogue

| Script | Purpose | Required Args |
|---|---|---|
| [`scripts/write-pr-labeler.py`](scripts/write-pr-labeler.py) | Write `.github/workflows/pr-labeler.yml` AND `.github/labeler-config.yml` | None (all optional with defaults) |

### 3.2 Invocation

```bash
python3 .agents/skills/github-pr-labeler/scripts/write-pr-labeler.py \
    --repo-root /path/to/repo
```

**Arguments:**

| Flag | Default | Purpose |
|---|---|---|
| `--repo-root` | `.` | Root of the target repository |

### 3.3 Output Files

**`.github/workflows/pr-labeler.yml`:**

```yaml
name: PR Labeler

on:
  pull_request:
    types: [opened, edited, synchronize]

jobs:
  label:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/labeler@v5
        with:
          configuration-path: .github/labeler-config.yml
```

**`.github/labeler-config.yml`:**

```yaml
skill:
  - changed-files:
    - any-glob-to-any-file: ['.agents/skills/**']
documentation:
  - changed-files:
    - any-glob-to-any-file: ['docs/**']
ci:
  - changed-files:
    - any-glob-to-any-file: ['.github/**']
script:
  - changed-files:
    - any-glob-to-any-file: ['scripts/**']
```

### 3.4 Label Mapping Table

| Label | Glob Pattern | Description |
|---|---|---|
| `skill` | `.agents/skills/**` | Changes to skill definitions |
| `documentation` | `docs/**` | Documentation changes |
| `ci` | `.github/**` | CI/CD workflow changes |
| `script` | `scripts/**` | Script changes |

### 3.5 Exit Codes

| Code | Meaning |
|---|---|
| `0` | Both files written successfully |
| `1` | Write error (permissions, invalid path) |

## 4. Composition by Higher-Level Skills

| Composer | Purpose |
|----------|---------|
| [`github-workflows`](../github-workflows/SKILL.md) | C4 — calls this skill for full workflow assembly |
| [`github-repo-publish`](../github-repo-publish/SKILL.md) | C7 — calls this skill during publish orchestration |

## 5. Related Skills

- [`github-workflow-creation`](../github-workflow-creation/SKILL.md) — general workflow authoring
- [`github-ci-markdown-lint`](../github-ci-markdown-lint/SKILL.md) — companion CI workflow
- [`github-ci-python-lint`](../github-ci-python-lint/SKILL.md) — companion CI workflow
