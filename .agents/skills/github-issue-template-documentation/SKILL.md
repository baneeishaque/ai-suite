---
name: github-issue-template-documentation
description: Base skill — writes `.github/ISSUE_TEMPLATE/documentation.yml` for standardized Documentation Request issue templates in GitHub repositories.
category: GitHub-Community
---

# GitHub Issue Template — Documentation Skill (v1)

> **Skill ID:** `github-issue-template-documentation`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)
> **Layer:** Base

## 1. When to Apply

Use this skill — or a higher-level composer of it — whenever the agent must scaffold a **Documentation Request** issue template into a GitHub repository. Typical triggers:

- "Add a documentation request template to the repo."
- "Set up GitHub issue templates for the project."
- "Create the standard documentation template in `.github/ISSUE_TEMPLATE/`."

**Anti-pattern:** If the agent needs a **Bug Report** or **Feature Request** template instead, use the respective sibling skills. This skill deals exclusively with `documentation.yml`.

## 2. Environment

- Python 3.10+ (`python3` on PATH, or resolve via `mise` per workspace convention).
- The target repository directory (default: current working directory).
- Write permission to create `.github/ISSUE_TEMPLATE/documentation.yml`.

## 3. Operational Logic

### 3.1 Script catalogue

| Script | Purpose | Required args | Behavior |
|---|---|---|---|
| [`scripts/write-documentation-template.py`](scripts/write-documentation-template.py) | Generate `documentation.yml` with What is Missing, Suggested Location, and Examples or References fields. | `--repo-root <path>` (default `.`) | Writes file to `<repo-root>/.github/ISSUE_TEMPLATE/documentation.yml`. Prints confirmation to stdout. Exits 0 on success, 1 on error. |

### 3.2 Invocation example

```bash
SCRIPTS_DIR=.agents/skills/github-issue-template-documentation/scripts

# Write to current directory
python3 "$SCRIPTS_DIR"/write-documentation-template.py

# Write to a specific repo
python3 "$SCRIPTS_DIR"/write-documentation-template.py --repo-root /path/to/repo
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
