# OpenCode Session YAML Transcript Extractor — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need the per-turn transcript of an opencode logger-plugin session log
  (`.opencode/logs/ses_<id>.yaml` monolithic, or `ses_<id>/` per-turn
  directory) as chronological JSONL — including the user's messages and the
  assistant's thinking, not just tool calls.
- You are building or running a session-analysis workflow (problem/solution
  reconstruction, summarization, debugging forensics) that needs narrative
  context alongside the tool-call sequence.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
the record contract, CLI flags, filter semantics, and exit codes. Do NOT
execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the transcript record contract and CLI.
- [`opencode-session-yaml-tool-call-extractor`](../opencode-session-yaml-tool-call-extractor/SKILL.md) —
  parallel base emitting tool-call-only JSONL over the same YAML layouts.
- [`opencode-session-problem-solution-workflow-analysis`]
  (../opencode-session-problem-solution-workflow-analysis/SKILL.md) —
  composer consuming this base for problem/solution/workflow reconstruction.
