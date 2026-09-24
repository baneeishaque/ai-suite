# Changelog — opencode-session-bash-file-ops-classifier

## v3 (2026-07-31)

- Fixed false positives in redirect-write classification (`REDIRECT_RE`): fd redirects (`2>`) no longer match, targets must look like a path (contain `/`, `.`, or start with `~`), `/dev/null` is explicitly skipped, and backslash-escaped targets (`\"...`, `\$d`) are rejected — so stderr suppression (`2>/dev/null`), prose like `<path>` inside printf format strings, and shell text embedded in quoted programs (`python3 -c "... printf ... > path"`) no longer produce `bash-op:overwrite` rows. Known residual limit: an *unescaped* path inside a quoted program still matches (indistinguishable from a real quoted redirect).

## v2 (2026-07-31)

- Added `--yaml <path>` mode — extracts from opencode logger-plugin YAML logs (monolithic .yaml file OR per-turn directory) via the `opencode-session-yaml-tool-call-extractor` base skill, emitting the same JSONL contract as the .md mode.
