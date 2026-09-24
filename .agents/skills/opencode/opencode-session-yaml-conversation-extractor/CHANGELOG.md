# Changelog

## 2026-08-11

- v1 creation — base primitive extracting a conversation-only YAML transcript
  from opencode logger-plugin YAML session logs. Keeps `user.text` and
  `assistant[].response` (plus `assistant[].agent` only when value is
  `compaction`); drops `thinking`, `tool_calls`, `model`, `time`, `duration*`.
  Preserves YAML structure via ruamel.yaml round-trip (comments, scalar styles,
  key ordering, `---` separators). One `<stem>-transcript.yaml` per input
  file, written to a `transcripts/` subfolder. Script logic generalizes the
  ad-hoc conversation-filter workflow executed during session
  `ses_012fd48f0ffedPT1brWW8fcezW`.
