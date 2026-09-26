# OpenCode Session Bash Write Extractor — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You have an opencode session export (`.md` format) containing Tool: bash calls
- You need to extract file write operations from heredoc commands (`cat > file << 'EOF'`)
- The target file(s) to recover are specified via glob pattern
- You want a domain-agnostic primitive — not specific to any particular file

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- Composer: [`file-recovery-from-session`](../file-recovery-from-session/SKILL.md) —
  consumes this base skill for recovering bash-created files
- Related: [`opencode-session-write-extractor`](../opencode-session-write-extractor/SKILL.md) —
  parallel base skill for Tool: write payload extraction
- Related: [`opencode-session-edit-extractor`](../opencode-session-edit-extractor/SKILL.md) —
  parallel base skill for Tool: edit payload extraction
- Composer: [`session-full-change-audit`](../session-full-change-audit/SKILL.md) —
  includes bash heredoc writes in unified change audits with `_source: "bash-write"`
