---
name: github-ci-markdown-lint
description: Base skill — write a GitHub Actions workflow for markdown linting via `DavidAnson/markdownlint-cli2-action`. Single-purpose workflow generator for CI markdown quality enforcement.
category: CI/CD & DevOps
layer: Base
script: scripts/write-markdown-lint-job.py
---

# GitHub CI — Markdown Lint Skill (v1)

> **Skill ID:** `github-ci-markdown-lint`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)
> **Layer:** Base

## 1. When to Apply

Use this skill whenever an agent must **create or update** a GitHub Actions workflow that lints Markdown files via `markdownlint-cli2` across a repository.

**Triggers:**

- "Add a markdown lint CI workflow."
- "Set up markdown linting in CI."
- "Create a workflow to check Markdown formatting."

**Anti-trigger:** If Python linting is also needed, use [`github-ci-python-lint`](../github-ci-python-lint/SKILL.md) separately or combine via a higher-level composer.

## 2. Environment & Dependencies

| Tool | Purpose | Verification |
|---|---|---|
| `python3` (3.10+) | Script engine | `python3 --version` |

The generated workflow requires the `DavidAnson/markdownlint-cli2-action@v19` GitHub Action (publicly available on the marketplace).

## 3. Operational Logic

### 3.1 Script Catalogue

| Script | Purpose | Required Args |
|---|---|---|
| [`scripts/write-markdown-lint-job.py`](scripts/write-markdown-lint-job.py) | Write `.github/workflows/ci-markdown-lint.yml` | None (all optional with defaults) |

### 3.2 Invocation

```bash
python3 .agents/skills/github-ci-markdown-lint/scripts/write-markdown-lint-job.py \
    --repo-root /path/to/repo \
    --runner ubuntu-24.04
```

**Arguments:**

| Flag | Default | Purpose |
|---|---|---|
| `--repo-root` | `.` | Root of the target repository |
| `--runner` | `ubuntu-24.04` | GitHub Actions runner OS label |

### 3.3 YAML Output

The script produces `.github/workflows/ci-markdown-lint.yml`:

```yaml
name: CI - Markdown Lint

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  lint-markdown:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Lint Markdown
        uses: DavidAnson/markdownlint-cli2-action@v19
        with:
          command: config
          globs: "**/*.md"
```

### 3.4 Exit Codes

| Code | Meaning |
|---|---|
| `0` | Workflow written successfully |
| `1` | Write error (permissions, invalid path) |

## 4. Composition by Higher-Level Skills

| Composer | Purpose |
|----------|---------|
| [`github-ci-lint`](../github-ci-lint/SKILL.md) | C2 — calls this skill for CI lint workflows |
| [`github-workflows`](../github-workflows/SKILL.md) | C4 — calls this skill for full workflow assembly |
| [`github-repo-publish`](../github-repo-publish/SKILL.md) | C7 — calls this skill during publish orchestration |

## 5. Related Skills

- [`github-ci-python-lint`](../github-ci-python-lint/SKILL.md) — companion base skill for Python linting CI
