# Changelog

## [1.0.0] - 2026-09-19

### Added
- Initial release of `renovate-dependent-branch-auto-rebase` composer skill
- Workflow script: `scripts/run-renovate-auto-rebase-workflow.py`
- Orchestrates `renovate-config-patterns` + `renovate-auto-rebase-detector` + `git-dependent-branch-restack-cascade`
- Auto mode: detects auto-rebase, updates config if needed, falls back to cascade
- Manual mode: direct cascade
- Dry-run mode for safe testing
- SKILL.md, AGENTS.md, CHANGELOG.md, TRACEABILITY.md