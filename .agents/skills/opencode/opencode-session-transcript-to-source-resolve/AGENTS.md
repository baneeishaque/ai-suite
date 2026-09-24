# OpenCode Session Transcript To Source Resolve — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You have free text referencing opencode logger session files — transcript
  paths (`ses_<id>/transcripts/NNN-<ts>-transcript.yaml`) or source logs
  (`ses_<id>/NNN-<ts>.yaml`) — and you need the ACTUAL source log file paths.
- The references carry compact `to N` range markers (e.g. `030-...-transcript.yaml to 36`)
  and you need every source log in the span.
- A consumer (machine analysis via the transcript/tool-call extractors) needs
  the durable source logs, but a transcript path is the only reference you have.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
reference syntax, resolution rules, CLI flags, and exit codes. Do NOT execute
any step without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the resolution rules and CLI contract.
- [`file-glob-sort-by-regex-capture`](../../file-glob-sort-by-regex-capture/SKILL.md) —
  consumed base: range expansion delegates to its `--min`/`--max` numeric-span filter.
- [`opencode-session-yaml-conversation-extractor`](../opencode-session-yaml-conversation-extractor/SKILL.md) —
  producer of the transcript artifacts this composer resolves away from.
- [`opencode-session-yaml-transcript-extractor`](../opencode-session-yaml-transcript-extractor/SKILL.md) —
  consumer of the SOURCE logs (the resolution target).
- [`opencode-session-yaml-tool-call-extractor`](../opencode-session-yaml-tool-call-extractor/SKILL.md) —
  consumer of the SOURCE logs (the resolution target).
