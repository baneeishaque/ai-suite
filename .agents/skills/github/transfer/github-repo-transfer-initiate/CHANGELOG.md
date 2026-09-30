# Changelog

## [1.0.0] - 2026-09-30

### Added

- Initial release of the `github-repo-transfer-initiate` base skill.
- `scripts/initiate-repo-transfers.py` — dry-run-by-default initiation of
  `POST /repos/<old>/<repo>/transfer` (202) with `--execute` gating; per-repo
  JSON records + acceptance-step note.
- `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`.
