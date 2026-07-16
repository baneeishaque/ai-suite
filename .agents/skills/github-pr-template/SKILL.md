---
name: github-pr-template
description: Base skill — writes `.github/PULL_REQUEST_TEMPLATE.md` for standardized Pull Request templates in GitHub repositories.
category: GitHub-Community
---

# GitHub PR Template Skill (v1)

> **Skill ID:** `github-pr-template`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)
> **Layer:** Base

## 1. When to Apply

Use this skill — or a higher-level composer of it — whenever the agent must scaffold a **Pull Request** template into a GitHub repository. Typical triggers:

- "Add a PR template to the repo."
- "Set up the standard pull request template."
- "Create `.github/PULL_REQUEST_TEMPLATE.md`."

**Anti-pattern:** If the agent needs an **issue template** instead (bug, feature, or documentation), use the respective sibling issue-template skills. This skill deals exclusively with the PR template.

## 2. Environment

- Python 3.10+ (`python3` on PATH, or resolve via `mise` per workspace convention).
- The target repository directory (default: current working directory).
- Write permission to create `.github/PULL_REQUEST_TEMPLATE.md`.

## 3. Operational Logic

### 3.1 Script catalogue

| Script | Purpose | Required args | Behavior |
|---|---|---|---|
| [`scripts/write-pr-template.py`](scripts/write-pr-template.py) | Generate `PULL_REQUEST_TEMPLATE.md` with Description, Related Issues, Type of Change checklist, and Contributor Checklist sections. | `--repo-root <path>` (default `.`) | Writes file to `<repo-root>/.github/PULL_REQUEST_TEMPLATE.md`. Prints confirmation to stdout. Exits 0 on success, 1 on error. |

### 3.2 Invocation example

```bash
SCRIPTS_DIR=.agents/skills/github-pr-template/scripts

# Write to current directory
python3 "$SCRIPTS_DIR"/write-pr-template.py

# Write to a specific repo
python3 "$SCRIPTS_DIR"/write-pr-template.py --repo-root /path/to/repo
```

### 3.3 Exit codes

| Code | Meaning |
|---|---|
| `0` | Template written successfully |
| `1` | Filesystem error (permissions, disk full, etc.) |

## 4. Composition by Higher-Level Skills

| Composer | Purpose |
|----------|---------|
| [`github-repo-templates`](../github-repo-templates/SKILL.md) | C1 — calls this skill as part of the template set |

## 5. Related Skills

- [`github-repo-templates`](../github-repo-templates/SKILL.md) — companion skill that manages the full suite of issue templates and the PR template together.
