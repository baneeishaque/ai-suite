# Changelog

## 2026-08-11

- v1 creation — base primitive extracting the per-turn transcript
  (session header, user text, assistant thinking, tool calls) from opencode
  logger-plugin YAML session logs as chronological JSONL. Script logic
  generalizes the ad-hoc summarizer + narrative dumper used during
  that analysis.
