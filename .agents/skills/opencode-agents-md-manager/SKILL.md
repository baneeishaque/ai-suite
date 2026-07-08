---
name: opencode-agents-md-manager
description: Manage AGENTS.md rows in multi-session working trees — isolate, stage, and commit only the current session's rows while leaving other-session rows untouched.
category: General
---

# OpenCode AGENTS.md Manager (v1)

> **Skill ID:** `opencode-agents-md-manager`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)
> **Layer:** Composer

## Composition Rationale

This skill is a **composer**: it does NOT re-implement staging or commit
mechanics. It composes the hunk-based staging protocol from
[`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
with AGENTS.md-specific concerns:

1. **Multi-session coexistence** — AGENTS.md frequently accumulates rows
   from multiple concurrent sessions. Staging the whole file would commit
   other sessions' unfinished work.
2. **Row isolation** — Identifying which diff hunks belong to the current
   session vs other sessions via `git diff` analysis.
3. **Selective staging** — Using `git add -p` or the `--mode staged` flag
   to stage only the current session's rows.
4. **Post-commit verification** — Confirming committed rows are in HEAD
   while other-session rows remain unstaged.

The base
[`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
skill owns the generic commit workflow; this composer carries the
AGENTS.md-specific domain knowledge.

## Environment & Dependencies

| Requirement | Minimum | Notes |
|---|---|---|
| `git` | 2.x+ | For diff analysis, hunk staging, and verification |
| Python 3 | 3.10+ | For `git add -p` automation when hunks are complex |
| Read permission | — | To read AGENTS.md and identify rows |

## When to Use

- When AGENTS.md has been modified and needs to be committed, but the
  file also contains rows from other in-progress sessions.
- When only a subset of AGENTS.md changes should enter the current commit.
- After creating or enriching a skill that needs registration in
  AGENTS.md.

Do NOT apply when:

- AGENTS.md has changes from only one session (the whole file can be
  staged normally per `git-atomic-commit-construction`).
- AGENTS.md changes are already cleanly isolated in their own commit.

## Step-by-Step Procedure

### Step 1 — Detect All AGENTS.md Changes

```bash
git diff AGENTS.md
```

Identify each hunk by:

1. Reading the row content — each row follows the pattern
   `- <skill-folder-name>: <description>`.
2. Distinguishing the current session's rows from other sessions' rows.
   Rows from other sessions are typically unrelated to the current task.

### Step 2 — Stage Only Current-Session Rows

**Option A: `git add -p`** (recommended when hunks are few)

```bash
git add -p AGENTS.md
```

Use `y` (yes) for hunks containing current-session rows and `n` (no)
for other-session rows. Use `s` (split) if a single hunk mixes both.

**Option B: `--mode staged`** (when a helper script is available)

If the repository provides a row-staging script (e.g., `agents-md-stage-row.py`),
use the `--mode staged` flag to stage only rows matching the current
session identity:

```bash
python3 .agents/skills/git-atomic-commit-construction/scripts/agents-md-stage-row.py \
  --row-name <skill-name> \
  --mode staged \
  --file AGENTS.md
```

### Step 3 — Verify Isolation

```bash
git diff --cached -- AGENTS.md      # staged: should only show current-session rows
git diff AGENTS.md                  # unstaged: should only show other-session rows
```

If other-session rows appear in `git diff --cached`, unstage and retry
Step 2 with finer hunk granularity.

### Step 4 — Commit

Follow the
[`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
commit protocol:

```bash
git commit -m "feat(skill): register <skill-name> in AGENTS.md"
```

### Step 5 — Post-Commit Verification

```bash
git show HEAD -- AGENTS.md          # confirm committed rows are in HEAD
git diff AGENTS.md                  # confirm other-session rows remain unstaged
```

If other-session rows were accidentally committed, use
[`git-history-refinement`](../git-history-refinement/SKILL.md) to
remove them from the commit.

## SSOT Compliance

- The **commit staging protocol** is owned by
  [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  (§3a–§3f — hunk-based staging).
- The **pre-commit verification** is owned by
  [`pre-commit-verification-protocol`](../general/pre-commit-verification-protocol/SKILL.md).
- The **batch authorization and commit sequencing** is owned by
  [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  (§2g — batch-by-batch authorization).
- This skill does NOT redefine any of them — it sequences them into a
  AGENTS.md-specific workflow.

## Related Skills

- [`pre-commit-verification-protocol`](../general/pre-commit-verification-protocol/SKILL.md)
  — verification pipeline to run before staging.
- [`skill-factory`](../skill-factory/SKILL.md) — skill creation workflow
  that produces AGENTS.md rows needing registration.
- [`opencode-config-preserve`](../opencode-config-preserve/SKILL.md) —
  companion composer for OpenCode configuration preservation.

## Traceability

- Created: 2026-07-03
- Source: OpenCode config versioning & preservation session. The
  `--mode staged` technique was used during Commit 6 to register
  the `opencode-config-preserve` skill in AGENTS.md while preserving
  8 other-session rows in the working tree.
