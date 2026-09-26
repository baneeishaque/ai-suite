# OpenCode Session Bash Block Extractor — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You have an opencode session export (`.md` format) containing `Tool: bash`
  blocks
- You need to extract the raw command strings from those blocks for analysis,
  classification, or auditing
- You are building a downstream tool that needs to process bash commands
  from sessions

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
all mandates, scripts, and verification steps. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`opencode-session-bash-file-ops-classifier`](../opencode-session-bash-file-ops-classifier/SKILL.md)
  — Downstream classifier consuming this skill's output
- [`session-file-ops-audit`](../session-file-ops-audit/SKILL.md)
  — Composer orchestrating bash block extraction + classification + report
- [`session-full-change-audit`](../session-full-change-audit/SKILL.md)
  — Higher-level composer that pipes this skill's output into the classifier,
    then merges into unified JSONL stream
