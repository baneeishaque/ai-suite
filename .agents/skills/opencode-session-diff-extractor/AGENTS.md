# OpenCode Session Diff Extractor — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You have an opencode session export (`.md` format) containing tool calls
- You need to extract `git diff` output blocks from that session
- The target file(s) to recover are specified via glob pattern (e.g., `AGENTS.md`)
- You want a domain-agnostic primitive — not specific to any particular file

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- Composer: [`agents-md-recovery-from-session`](../agents-md-recovery-from-session/SKILL.md) — consumes this base skill for AGENTS.md-specific recovery
- Related: [`git-pre-execution-safety-stash`](../git-pre-execution-safety-stash/SKILL.md) — creates safety stashes before multi-commit sequences (prevents this class of loss)
- Related: [`git-history-refinement`](../git-history-refinement/SKILL.md) — for splitting/reconstructing commits if recovery reveals history issues
- Composer: [`session-full-change-audit`](../session-full-change-audit/SKILL.md) —
  higher-level composer covering all change sources (though this skill's
  git-diff extraction is used only by agents-md-recovery)