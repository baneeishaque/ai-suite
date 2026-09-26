# Session File Ops Audit — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You have an opencode session export and need to audit every file
  operation performed during the session (writes, deletes, copies, moves)
- You need a summary report of what bash commands affected the filesystem

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure.

## Cross-References

- [`opencode-session-bash-block-extractor`](../opencode-session-bash-block-extractor/SKILL.md)
  — Base skill for extracting bash command strings
- [`opencode-session-bash-file-ops-classifier`](../opencode-session-bash-file-ops-classifier/SKILL.md)
  — Base skill for classifying commands into file operation types
- [`file-recovery-from-session`](../file-recovery-from-session/SKILL.md)
  — For actually recovering written files from a session
- [`session-full-change-audit`](../session-full-change-audit/SKILL.md)
  — Higher-level composer covering all change sources (superset of this skill's bash-only scope)
