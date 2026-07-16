---
name: planning-artifact-naming
description: >-
  Convention for naming planning artifacts (task, implementation-plan,
  commit-preview, walkthrough, sub-plan) with opencode session identity
  for traceability and machine-readable sort order.
category: General
---

# Planning Artifact Naming Convention (v1)

This skill defines the naming convention for all planning artifacts
generated during AI-agent sessions. The convention embeds session
identity (human-readable name + machine-readable ID) directly into
each filename, ensuring artifacts are self-traceable to their source
conversation and sort chronologically at the filesystem level.

The convention was established during an OpenCode config preservation
session and generalised here for reuse across all agent workflows.

***

## 1. Formula

```text
docs/<date>_<session-id>_<session-name-slug>_<artifact-type>_v<version>.md
```

All planning artifacts MUST be stored under `docs/` in the main
repository (per
[Traceability Portability Mandate](../../../../ai-agent-rules/ai-rule-standardization-rules.md)).

### 1.1 Part Reference

| Part | Required | Format | Example |
| :--- | :--- | :--- | :--- |
| `date` | Always | `YYYY-MM-DD` | `2026-07-03` |
| `session-id` | Always | Full opencode session ID (without `ses_` prefix) | `0dd0a9769ffe9VhJz3qA3VnZNV` |
| `session-name-slug` | Always | Kebab-case of the opencode session name | `opencode-config-versioning-preservation` |
| `artifact-type` | Always | Kebab-case type identifier | `implementation-plan` |
| `version` | Versioned only | `v<integer>` | `v3` |
| Extension | Always | `.md` | `.md` |

### 1.2 Separator Rule

- **Underscore** (`_`) separates every top-level part.
- **Hyphen** (`-`) is used only WITHIN a part (date-separator,
session-name-slug, artifact-type).

Correct:

```text
2026-07-03_0dd0a9769ffe9VhJz3qA3VnZNV_opencode-config-versioning-preservation_implementation-plan_v3.md
```

Incorrect (hyphen between parts — ambiguous boundaries):

```text
2026-07-03-0dd0a9769ffe9VhJz3qA3VnZNV-opencode-config-versioning-preservation-implementation-plan-v3.md
```

Incorrect (truncated ID, missing date, missing name):

```text
ses_0dd0a9_task.md
```

### 1.3 `ses_` Prefix Handling

The opencode session ID natively starts with `ses_` (e.g.,
`ses_0dd0a9769ffe9VhJz3qA3VnZNV`). The `ses_` prefix MUST be omitted
from the filename because the filename context already identifies it
as a session ID:

- Correct: `0dd0a9769ffe9VhJz3qA3VnZNV`
- Incorrect: `ses_0dd0a9769ffe9VhJz3qA3VnZNV`

The full 26+ character ID MUST be used — NOT a truncated form.

***

## 2. Artifact Types

### 2.1 Registered Types

| Artifact Type | Versioned? | Purpose |
| :--- | :--- | :--- |
| `task` | No (live checklist) | Track progress of the current session's objectives |
| `implementation-plan` | Yes | Detailed step-by-step plan for executing a goal |
| `commit-preview` | Yes | Preview of commits to be executed |
| `walkthrough` | Yes | Post-execution record of steps taken and decisions made |
| `skill-creation-plan` | Yes | Sub-plan for creating a new skill |
| `skill-documentation-plan` | Yes | Sub-plan for enriching existing skills |
| `audit-log` | Yes | Record of an audit or inspection |
| `summary` | Yes | Session summary or retrospective |

New artifact types MAY be added as workflows evolve; each new type
MUST be registered here.

### 2.2 Versioning Rules

1. NEW artifacts start at `v1`.
2. When content is updated, increment the version: `v1` → `v2` → `v3`.
3. OLD versions are NEVER overwritten or deleted. The old file remains
   alongside the new one.
4. For `task` (unversioned), the file is edited in place — it is a live
   checklist, not a historical record.
5. Different artifact types have INDEPENDENT version counters — an
   implementation-plan at v3 and its corresponding commit-preview at v2
   is valid.

***

## 3. Examples

The following files were created during the originating session and
serve as canonical examples:

```text
docs/2026-07-03_0dd0a9769ffe9VhJz3qA3VnZNV_opencode-config-versioning-preservation_task.md
docs/2026-07-03_0dd0a9769ffe9VhJz3qA3VnZNV_opencode-config-versioning-preservation_implementation-plan_v3.md
docs/2026-07-03_0dd0a9769ffe9VhJz3qA3VnZNV_opencode-config-versioning-preservation_commit-preview_v2.md
docs/2026-07-03_0dd0a9769ffe9VhJz3qA3VnZNV_opencode-config-versioning-preservation_skill-documentation-plan_v1.md
```

All four share the same session identity (date + session-id +
session-name-slug) and differ only in artifact-type and version.

***

## 4. Related Skills

- [`skill-factory`](../../skill-factory/SKILL.md) — Consumes this naming
  convention when generating planning artifacts for new skills.
- [`markdown-generation`](../../markdown-generation/SKILL.md) — Markdown
  formatting standards that generated artifacts must obey.
- [`planning-artifact-lifecycle`](../planning-artifact-lifecycle/SKILL.md) —
  Lifecycle management for planning artifacts (versioning triggers, CAM §7.1
  enforcement, deletion protocol). Companion base skill that covers *how to
  manage* artifacts once named.

***

## 5. Traceability

- Created: 2026-07-03
- Source: OpenCode config versioning & preservation session
  (`0dd0a9769ffe9VhJz3qA3VnZNV`). The convention was iteratively refined
  through conversation: underscore separators, omission of `ses_` prefix,
  date prefix for task files, independent versioning for artifact types.
