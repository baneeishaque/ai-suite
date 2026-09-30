# Changelog

## [1.0.0] - 2026-09-30

### Added

- Initial release of the `github-repo-state-fingerprint` base skill.
- `scripts/repo-state-fingerprint.py` — `capture` / `compare` subcommands;
  curated compare keys with volatile metrics ignored by default (`--strict` to
  include); cross-owner comparison via `--owner` override; snapshot files +
  JSONL verdicts; read-only.
- `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`.
