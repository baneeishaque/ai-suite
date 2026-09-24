# Changelog

## 2026-08-12

- v1 creation — composer that resolves opencode session transcript references
  (single or `to N` ranges) in free text to the actual source log files under
  the session directory. Strips the `-transcript` suffix and ascends out of
  `transcripts/` for transcript-form references; leaves source-form references
  unchanged. `--expand` emits one absolute source-log path per line, delegating
  numeric-span range listing to the `file-glob-sort-by-regex-capture` base
  primitive's `--min`/`--max` filter (never re-implementing the
  glob+regex+sort pipeline). Exit codes: 0 success, 1 no references found,
  2 usage/base-script-missing, 3 session-dir/source-file not found (`--expand`).
