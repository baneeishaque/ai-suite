# Changelog

## [1.0.0] - 2026-09-30

### Added

- Initial release of the `github-repo-transfer-destination-conflict-check`
  composite skill.
- `scripts/check-destination-conflicts.py` — destination-availability gate over
  `github-repo-name-conflict-check`; streams per-name verdicts and emits the
  `pass` / `block` gate summary.
- `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`.
