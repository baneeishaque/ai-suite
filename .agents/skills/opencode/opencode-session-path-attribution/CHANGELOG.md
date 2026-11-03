# Changelog — opencode-session-path-attribution

## v1.1 (2026-11-04)

- Document the in-flight-turn exclusion: `NNN-pending-*.yaml` is not scanned,
  so a path first cited in the live turn yields `no_match`; record the pending
  YAML path and call index directly and rely on the archived re-run for the
  positive attribution anchor.

## v1 (2026-08-08)

- Initial release — cross-session sweep, per-turn extractor composition,
  token matching with exit-code contract, own write to logger-lookup.
