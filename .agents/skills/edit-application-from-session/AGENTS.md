# Edit Application from Session — Composer Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- A file needs its content restored to a version that existed during an
  OpenCode session
- An OpenCode session export (`.md` format) exists containing `Tool: edit`
  blocks that modified the file
- You need to replay `Tool: edit` operations from a session onto existing
  files (e.g., after a git reset, or on a different branch)

## Operational Procedure

Load [`SKILL.md`](SKILL.md) for the complete edit-application workflow:

1. Extract edit payloads from session via
   [`opencode-session-edit-extractor`](../opencode-session-edit-extractor/SKILL.md)
2. Apply `oldString → newString` replacement to each target file
3. Verify replacement occurred

## Cross-References

- [`opencode-session-edit-extractor`](../opencode-session-edit-extractor/SKILL.md)
  — Base primitive that does the extraction work
- [`file-recovery-from-session`](../file-recovery-from-session/SKILL.md)
  — Parallel composer for Tool: write and Tool: bash heredoc recovery
- [`agents-md-recovery-from-session`](../agents-md-recovery-from-session/SKILL.md)
  — Parallel composer for AGENTS.md recovery via git diffs
- [`session-full-change-audit`](../session-full-change-audit/SKILL.md)
  — Higher-level composer including edit-payload scope in unified change audits
