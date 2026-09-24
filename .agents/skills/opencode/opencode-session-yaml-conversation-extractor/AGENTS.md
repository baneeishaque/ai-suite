# OpenCode Session YAML Conversation Extractor — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need a **conversation-only YAML transcript** of an opencode
  logger-plugin session log (`.opencode/logs/ses_<id>.yaml` monolithic, or
  `ses_<id>/` per-turn directory) — the user's messages and the assistant's
  replies, with `thinking`, `tool_calls`, `model`, and timing fields stripped.
- You want the output to remain valid YAML that preserves the original
  structure (comments, scalar styles, key ordering) via ruamel.yaml round-trip,
  rather than converting to JSONL.
- You are archiving, reviewing, or publishing a session's dialogue and need a
  readable, structure-preserving transcript rather than an analysis-oriented
  JSONL feed.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
field rules, CLI flags, exit codes, and output naming. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the field rules and CLI contract.
- [`opencode-session-yaml-transcript-extractor`](../opencode-session-yaml-transcript-extractor/SKILL.md) —
  parallel base emitting all-fields JSONL (header, user, thinking, tool calls)
  over the same YAML layouts; preferred when the full narrative including
  thinking is required.
- [`opencode-session-yaml-tool-call-extractor`](../opencode-session-yaml-tool-call-extractor/SKILL.md) —
  parallel base emitting tool-call-only JSONL.
