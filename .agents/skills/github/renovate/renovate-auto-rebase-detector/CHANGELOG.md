# Changelog

## [1.0.0] - 2026-09-19

### Added
- Initial release of `renovate-auto-rebase-detector` base skill
- Detection script: `scripts/detect-renovate-auto-rebase.py`
- Implements full `rebaseWhen` semantics per Renovate docs
- Git branch protection and merge queue detection via `gh` CLI
- SKILL.md, AGENTS.md, CHANGELOG.md, TRACEABILITY.md