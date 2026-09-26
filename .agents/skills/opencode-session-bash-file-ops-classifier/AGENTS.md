# OpenCode Session Bash File Ops Classifier — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You have JSONL lines with `{"command": "..."}` from an opencode session
- You need to classify bash commands as file operations (write, delete,
  copy, move) or non-operational

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure.

## Cross-References

- [`opencode-session-bash-block-extractor`](../opencode-session-bash-block-extractor/SKILL.md)
  — Upstream block extractor
- [`session-file-ops-audit`](../session-file-ops-audit/SKILL.md)
  — Composer using this skill for end-to-end audit
- [`session-full-change-audit`](../session-full-change-audit/SKILL.md)
  — Composer that pipes block-extractor output into this classifier,
    then merges classified ops into unified JSONL stream
