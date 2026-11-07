---
name: planning-artifact-naming
description: >-
  Convention for naming planning artifacts (task, implementation-plan,
  commit-preview, walkthrough, sub-plan) with opencode session identity
  for traceability and machine-readable sort order.
category: General
---

# Planning Artifact Naming Convention (v1)

This skill defines layout profiles for planning artifacts generated during
AI-agent sessions. Profiles carry session identity in the filename or parent
directory, keeping each artifact traceable to its source conversation and
chronologically organized within the selected profile.

The convention was established during an OpenCode config preservation
session and generalised here for reuse across all agent workflows.

***

## 1. Formula

Select and record a layout profile before creating an artifact:

- **Legacy flat**: the default unless the owning repository selects another
  profile. Its formula and filename rules are defined in §§1.1–1.3 below.
- **Resolver-backed nested**: an explicit local profile described in §1.4.
  It places session identity in directories and delegates path construction
  to the existing docs resolver.

A profile choice does not rename existing artifacts. Apply the registered
artifact types and lifecycle rules to either profile.

The legacy flat formula is:

```text
docs/<date>_<session-id>_<session-name-slug>_<artifact-type>_v<version>.md
```

All planning artifacts MUST be stored under `docs/` in the main
repository (per
[Traceability Portability Mandate](../../../../../ai-agent-rules/ai-rule-standardization-rules.md)).

### 1.1 Part Reference

| Part | Required | Format | Example |
| :--- | :--- | :--- | :--- |
| `date` | Always | `YYYY-MM-DD` | `2026-07-03` |
| `session-id` | Always | Full opencode session ID (without `ses_` prefix) | `<session-id>` |
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
2026-07-03_<session-id>_opencode-config-versioning-preservation_implementation-plan_v3.md
```

Incorrect (hyphen between parts — ambiguous boundaries):

```text
2026-07-03-<session-id>-opencode-config-versioning-preservation-implementation-plan-v3.md
```

Incorrect (truncated ID, missing date, missing name):

```text
<session-id>_task.md
```

### 1.3 `ses_` Prefix Handling

The opencode session ID natively starts with `ses_` (e.g., `ses_<session-id>`). The `ses_` prefix MUST be omitted from
the filename because the filename context already identifies it as a session ID:

- Correct: `<session-id>`
- Incorrect: `ses_<session-id>`

The full 26+ character ID MUST be used — NOT a truncated form.

Artifacts carrying AI-agent session IDs (any assistant or tool) are local-only; never commit them.
Committed documents MUST NOT reference them — explain the relevant context self-containedly (see skill-factory §2.2).

### 1.4 Resolver-Backed Nested Profile

```text
docs/<session-id>/<date>/<purpose>/<artifact>[_v<version>]_<time>.<ext>
```

Use the existing
[`resolve-docs-path.py`](../../file/scratch-artifact-naming/scripts/resolve-docs-path.py)
helper hosted by `scratch-artifact-naming`; this skill owns the planning-layout
policy. Do not reproduce the path-construction logic in another script.

- `session-id` is the full runtime-verified ID without the `ses_` prefix.
  Resolve and verify it through `opencode-current-session-id` before passing it;
  the docs resolver does not replace the pending-marker or phrase-verification gate.
- `date` is a `YYYY-MM-DD` directory; `purpose` and `artifact` are lowercase-kebab
  values. Purpose is an explicit task label, not an inferred session title.
- Supply `--version` for versioned artifact types; omit it for live task files.
- `time` is `HH-MM-SS-mmm_TZ`. The default timezone is `Asia/Kolkata`;
  `--timezone` selects another IANA zone, and invalid zones are rejected.
- `--date` and `--timestamp` provide explicit overrides; the timestamp override
  is used verbatim. `--ext` is the alphanumeric extension without its dot.
- The helper prints the absolute filename, including its extension. It creates
  parent directories by default; `--no-mkdir` prints the path without creating them.

```bash
python3 .agents/skills/general/file/scratch-artifact-naming/scripts/resolve-docs-path.py \
    --repo "<repo-root>" --purpose "<purpose>" --artifact commit-preview \
    --version 1 --ext md --session-id "<verified-session-id>"
```

Keep these artifacts local-only. Record the chosen profile in the artifact,
retain earlier versions, and use `planning-artifact-lifecycle` for retirement.

***

## 2. Artifact Types

### 2.1 Registered Types

| Artifact Type | Versioned? | Purpose |
| :--- | :--- | :--- |
| `task` | No (live checklist) | Track progress of the current session's objectives |
| `implementation-plan` | Yes | Detailed step-by-step plan for executing a goal |
| `implementation-plan-<topic>` | Yes | Topic-scoped variant used when one session produces MULTIPLE independent implementation plans; `<topic>` is a kebab-case slug disambiguating the plan (e.g. `implementation-plan-acers-audit-history`). The version counter is independent per topic |
| `commit-preview` | Yes | Preview of commits to be executed |
| `walkthrough` | Yes | Post-execution record of steps taken and decisions made |
| `walkthrough-<topic>` | Yes | Topic-scoped variant used when one session produces multiple walkthroughs; `<topic>` is a kebab-case slug disambiguating the record (mirrors `implementation-plan-<topic>`) |
| `skill-creation-plan` | Yes | Sub-plan for creating a new skill |
| `skill-documentation-plan` | Yes | Sub-plan for enriching existing skills. Produced by [`skill-library-gap-closure`](../../skill-dev/skill-library-gap-closure/SKILL.md) when a gap register routes rows to enrichment rather than creation |
| `audit-log` | Yes | Record of an audit or inspection |
| `summary` | Yes | Session summary or retrospective |

New artifact types MAY be added as workflows evolve; each new type
MUST be registered here.

### 2.2 Versioning Rules

1. NEW artifacts start at `v1`.
2. When content is updated, increment the version: `v1` → `v2` → `v3`.
3. OLD versions are NEVER erased by creation of a new one. The old file
   remains alongside the new one by default; however a superseded
   version MAY be intentionally retired ONLY through the authorized
   path — coverage audit FULL + explicit user consent — via the composer
   [`planning-superseded-version-retirement`](../planning-superseded-version-retirement/SKILL.md)
   (macOS: `trash`, never `rm`).
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
docs/2026-07-03_<session-id>_opencode-config-versioning-preservation_task.md
docs/2026-07-03_<session-id>_opencode-config-versioning-preservation_implementation-plan_v3.md
docs/2026-07-03_<session-id>_opencode-config-versioning-preservation_commit-preview_v2.md
docs/2026-07-03_<session-id>_opencode-config-versioning-preservation_skill-documentation-plan_v1.md
```

All four share the same session identity (date + session-id +
session-name-slug) and differ only in artifact-type and version.

***

## 4. Related Skills

- [`skill-factory`](../../../skill-factory/SKILL.md) — Consumes this naming
  convention when generating planning artifacts for new skills.
- [`markdown-generation`](../../../markdown-generation/SKILL.md) — Markdown
  formatting standards that generated artifacts must obey.
- [`planning-artifact-lifecycle`](../planning-artifact-lifecycle/SKILL.md) —
  Lifecycle management for planning artifacts (versioning triggers, CAM §7.1
  enforcement, deletion protocol). Companion base skill that covers *how to
  manage* artifacts once named.
- [`planning-version-coverage-audit`](../planning-version-coverage-audit/SKILL.md) —
  Mandatory coverage gate used before a superseded version may be
  intentionally retired (§2.2 rule 3).
- [`planning-superseded-version-retirement`](../planning-superseded-version-retirement/SKILL.md) —
  Composer owning the authorized retirement path (coverage FULL + user
  consent; macOS `trash`, never `rm`).

***

## 5. Traceability

See [TRACEABILITY.md](TRACEABILITY.md).

## 6. Changelog

See [CHANGELOG.md](CHANGELOG.md).
