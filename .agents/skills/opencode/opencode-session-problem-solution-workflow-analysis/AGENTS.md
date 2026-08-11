# OpenCode Session Problem-Solution-Workflow Analysis — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are given opencode logger-plugin session log files
  (`.opencode/logs/ses_<id>.yaml` or `ses_<id>/` per-turn directories) and
  asked to identify the problem, its solution, and the entire workflow
  executed in that session.
- You need a deterministic chronological report of a session's user
  messages, assistant thinking, and tool calls, with clearly marked
  sections for the analysis conclusions.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
the 7-step analysis procedure, judgement guidance, and script CLI
contract. Do NOT execute any step without first loading `SKILL.md` — this
bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the analysis procedure and CLI.
- [`opencode-session-yaml-transcript-extractor`](../opencode-session-yaml-transcript-extractor/SKILL.md) —
  base skill composed by this composer (transcript JSONL input).
- [`opencode-session-yaml-tool-call-extractor`](../opencode-session-yaml-tool-call-extractor/SKILL.md) —
  parallel base for tool-call-only extraction.
