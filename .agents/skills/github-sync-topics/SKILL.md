---
name: github-sync-topics
description: Base skill — write a GitHub Actions workflow that syncs repository topics from a Markdown table in README.md. Topics are extracted from a `## Topics` section containing backtick-delimited tags in a table.
category: CI/CD & DevOps
layer: Base
script: scripts/write-topics-sync-workflow.py
---

# GitHub Sync Topics Skill (v1)

> **Skill ID:** `github-sync-topics`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)
> **Layer:** Base

## 1. When to Apply

Use this skill whenever an agent must **create or update** a GitHub Actions
workflow that synchronizes a repository's topics from a Markdown table in
`README.md`.

**Triggers:**

- "Sync repo topics from README."
- "Keep repository topics in sync with a topics table in README."
- "Create a workflow that reads topics from README and updates the repo."

**Anti-trigger:** If description sync is also needed, use
[`github-sync-description`](../github-sync-description/SKILL.md). For a
combined sync, a higher-level `github-sync` composer should aggregate both.

## 2. Topic Table Parsing Pattern

The workflow extracts topics from `README.md` using a `## Topics` section with a Markdown table:

```markdown
## Topics

| Topic | Description |
|---|---|
| `agent-skills` | Agent Skills framework |
| `devops` | DevOps automation |
| `python` | Python tooling |
```

The embedded Python script:

1. Searches for a `## Topics` heading followed by a Markdown table
2. Extracts all backtick-delimited tags (`\`tag-name\``) from that table
3. Joins them with commas for the workflow step output
4. Exits with code 0 if no section is found (allowing empty topic list)

## 3. Environment & Dependencies

| Tool | Purpose | Verification |
|---|---|---|
| `python3` (3.10+) | Script engine | `python3 --version` |

The generated workflow requires `gh` CLI (authenticated via `GITHUB_TOKEN`) and Python 3 on the runner.

## 4. Operational Logic

### 4.1 Script Catalogue

| Script | Purpose | Required Args |
|---|---|---|
| [`scripts/write-topics-sync-workflow.py`](scripts/write-topics-sync-workflow.py) | Write `.github/workflows/sync-topics.yml` | None (all optional with defaults) |

### 4.2 Invocation

```bash
python3 .agents/skills/github-sync-topics/scripts/write-topics-sync-workflow.py \
    --repo-root /path/to/repo
```

**Arguments:**

| Flag | Default | Purpose |
|---|---|---|
| `--repo-root` | `.` | Root of the target repository |

### 4.3 YAML Output

The script produces `.github/workflows/sync-topics.yml`:

```yaml
name: Sync Topics

on:
  push:
    branches: [main, master]
    paths: ['README.md']

jobs:
  sync:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
      repository-projects: write
    steps:
      - uses: actions/checkout@v4
      - name: Extract topics
        id: extract
        run: |
          TOPICS=$(python3 -c "
import re
text = open('README.md').read()
table = re.search(r'## Topics.*?\n(\|.*\|\n)+', text, re.DOTALL)
if not table:
    sys.exit(0)
topics = re.findall(r'\`([a-z0-9-]+)\`', table.group())
print(','.join(topics), end='')
")
          echo "topics=$TOPICS" >> $GITHUB_OUTPUT
      - name: Update repo topics
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          IFS=',' read -ra TAGS <<< "${{ steps.extract.outputs.topics }}"
          for tag in "${TAGS[@]}"; do
            gh repo edit ${{ github.repository }} --add-topic "$tag"
          done
```

### 4.4 Exit Codes

| Code | Meaning |
|---|---|
| `0` | Workflow written successfully |
| `1` | Write error (permissions, invalid path) |

## 5. Composition by Higher-Level Skills

| Composer                                                            | Purpose                                              |
|---------------------------------------------------------------------|------------------------------------------------------|
| [`github-sync`](../github-sync/SKILL.md) | C3 — calls this skill for sync workflow orchestration |
| [`github-workflows`](../github-workflows/SKILL.md) | C4 — calls this skill for full workflow assembly |
| [`github-repo-publish`](../github-repo-publish/SKILL.md) | C7 — calls this skill during publish orchestration |

## 6. Related Skills

- [`github-sync-description`](../github-sync-description/SKILL.md) — companion base skill for description sync
- [`gh-repo-edit-metadata`](../gh-repo-edit-metadata/SKILL.md) — direct metadata editing via `gh`
