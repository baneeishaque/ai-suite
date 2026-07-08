# OpenCode Session Edit Extractor — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You have an opencode session export (`.md` format) containing tool calls
- You need to extract `Tool: edit` JSON payloads (`filePath`, `oldString`, `newString`) from that session
- The target file(s) to edit-apply are specified via glob pattern
- You want a domain-agnostic primitive — not specific to any particular file

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- Composer: [`edit-application-from-session`](../edit-application-from-session/SKILL.md) —
  consumes this base skill for applying edits to existing files
- Related: [`opencode-session-write-extractor`](../opencode-session-write-extractor/SKILL.md) —
  parallel base skill for Tool: write payload extraction
- Related: [`opencode-session-bash-write-extractor`](../opencode-session-bash-write-extractor/SKILL.md) —
  parallel base skill for bash heredoc file writes
- Composer: [`session-full-change-audit`](../session-full-change-audit/SKILL.md) —
  includes edit payloads in unified change audits with `_source: "edit"`
