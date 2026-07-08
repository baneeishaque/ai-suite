---
name: github-ci-python-lint
description: Base skill — write a GitHub Actions workflow for Python linting via `ruff`. Parameterized runner OS, Python version, and target glob. Single-purpose CI workflow generator.
category: CI/CD & DevOps
layer: Base
script: scripts/write-python-lint-job.py
---

# GitHub CI — Python Lint Skill (v1)

> **Skill ID:** `github-ci-python-lint`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)
> **Layer:** Base

## 1. When to Apply

Use this skill whenever an agent must **create or update** a GitHub Actions workflow that lints Python files with `ruff` across a repository.

**Triggers:**

- "Add a Python lint CI workflow."
- "Set up ruff linting in CI."
- "Create a workflow to check Python code style."

**Anti-trigger:** If markdown linting is also needed, use [`github-ci-markdown-lint`](../github-ci-markdown-lint/SKILL.md) separately or combine via a higher-level composer.

## 2. Environment & Dependencies

| Tool | Purpose | Verification |
|---|---|---|
| `python3` (3.10+) | Script engine | `python3 --version` |

The generated workflow installs `ruff` via `pip` during CI execution.

## 3. Operational Logic

### 3.1 Script Catalogue

| Script | Purpose | Required Args |
|---|---|---|
| [`scripts/write-python-lint-job.py`](scripts/write-python-lint-job.py) | Write `.github/workflows/ci-python-lint.yml` | None (all optional with defaults) |

### 3.2 Invocation

```bash
python3 .agents/skills/github-ci-python-lint/scripts/write-python-lint-job.py \
    --repo-root /path/to/repo \
    --runner ubuntu-24.04 \
    --python-version 3.12 \
    --target-glob ".agents/skills/"
```

**Arguments:**

| Flag | Default | Purpose |
|---|---|---|
| `--repo-root` | `.` | Root of the target repository |
| `--runner` | `ubuntu-24.04` | GitHub Actions runner OS label |
| `--python-version` | `3.12` | Python version for `actions/setup-python` |
| `--target-glob` | `.agents/skills/` | Glob pattern for `ruff check` |

### 3.3 YAML Output

The script produces `.github/workflows/ci-python-lint.yml`:

```yaml
name: CI - Python Lint

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  lint-python:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: python -m pip install --upgrade pip ruff
      - name: Run ruff
        run: ruff check .agents/skills/ --output-format github
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

- [`github-ci-markdown-lint`](../github-ci-markdown-lint/SKILL.md) — companion base skill for Markdown linting CI
