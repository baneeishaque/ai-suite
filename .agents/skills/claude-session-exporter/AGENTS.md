# Claude Session Exporter — Companion Bridge

## Purpose

This is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to export a Claude desktop or VS Code session JSONL file into readable markdown documentation.
- You need to separate content blocks by type
  (tool_use, tool_result, text, thinking, redacted_thinking) into matched and unmatched files.
- You want to archive, review, or analyze Claude session contents outside the Claude UI.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI contract,
output format, and all mandates. Do NOT execute any step without first loading `SKILL.md` —
this bridge is intentionally non-actionable.

## Cross-References

- [`jsonl-content-extractor`](../jsonl-content-extractor/SKILL.md) — base primitive used for mechanical extraction
- [`copilot-chat-history-analysis`](../copilot-chat-history-analysis/SKILL.md) — analogous skill for CSV chat history
