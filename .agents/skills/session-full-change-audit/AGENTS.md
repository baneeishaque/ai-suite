# Session Full Change Audit — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You have an opencode session export and need to audit ALL changes
  across every change type (Tool: write, Tool: edit, Tool: bash file
  ops, Tool: bash heredoc writes)
- You need a unified JSONL stream with source-type discrimination
  for downstream reporting, statistics, or CI pipelines
- You previously used `session-file-ops-audit` but now need coverage
  of non-bash changes as well

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`opencode-session-write-extractor`](../opencode-session-write-extractor/SKILL.md)
  — Base skill for Tool: write payload extraction
- [`opencode-session-edit-extractor`](../opencode-session-edit-extractor/SKILL.md)
  — Base skill for Tool: edit payload extraction
- [`opencode-session-bash-block-extractor`](../opencode-session-bash-block-extractor/SKILL.md)
  — Base skill for bash command extraction
- [`opencode-session-bash-file-ops-classifier`](../opencode-session-bash-file-ops-classifier/SKILL.md)
  — Base skill for classifying bash commands into file ops
- [`opencode-session-bash-write-extractor`](../opencode-session-bash-write-extractor/SKILL.md)
  — Base skill for bash heredoc write extraction
- [`session-file-ops-audit`](../session-file-ops-audit/SKILL.md)
  — Predecessor composer (bash file ops only)
- [`file-recovery-from-session`](../file-recovery-from-session/SKILL.md)
  — Parallel composer for recovering files from session exports
- [`edit-application-from-session`](../edit-application-from-session/SKILL.md)
  — Parallel composer for replaying edits
- [`session-audit-batch-orchestrator`](../session-audit-batch-orchestrator/SKILL.md)
  — Compositor that batches this skill across multiple session files and merges results
