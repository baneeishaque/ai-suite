# Changelog — opencode-session-bash-write-extractor

## v2 (2026-07-31)

- Added `--yaml <path>` mode — extracts from opencode logger-plugin YAML logs (monolithic .yaml file OR per-turn directory) via the `opencode-session-yaml-tool-call-extractor` base skill, emitting the same JSONL contract as the .md mode.
