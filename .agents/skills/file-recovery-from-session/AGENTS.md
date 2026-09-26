# File Recovery from Session — Composer Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- A file was accidentally deleted or overwritten during an OpenCode session
- An OpenCode session export (`.md` format) exists containing the original
  `Tool: write` payload or `Tool: bash` heredoc that created the file
- You need to recover one or more files from the session export

## Operational Procedure

Load [`SKILL.md`](SKILL.md) for the complete recovery workflow:

1. Extract write payloads from session (`--mode write`, `--mode bash`,
   or `--mode all`)
2. Write files to disk (original paths or redirected)
3. Verify content integrity
4. Report recovery summary

## Cross-References

- [`opencode-session-write-extractor`](../opencode-session-write-extractor/SKILL.md)
  — Base primitive for Tool: write extraction
- [`opencode-session-bash-write-extractor`](../opencode-session-bash-write-extractor/SKILL.md)
  — Base primitive for Tool: bash heredoc extraction
- [`opencode-session-edit-extractor`](../opencode-session-edit-extractor/SKILL.md)
  — Parallel base skill for Tool: edit extraction
- [`opencode-session-diff-extractor`](../opencode-session-diff-extractor/SKILL.md)
  — Parallel base skill for git diff extraction
- [`edit-application-from-session`](../edit-application-from-session/SKILL.md)
  — Parallel composer for applying Tool: edit payloads
- [`agents-md-recovery-from-session`](../agents-md-recovery-from-session/SKILL.md)
  — Parallel composer for AGENTS.md recovery via git diffs
- [`session-full-change-audit`](../session-full-change-audit/SKILL.md)
  — Higher-level composer including this skill's recovery scope in unified change audits
