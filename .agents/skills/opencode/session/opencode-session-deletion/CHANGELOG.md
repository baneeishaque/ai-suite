# Changelog — opencode-session-deletion

## [1.0.0] - 2026-11-04

- Initial composer: discover, confirm, delete (DB + logs + scratch + plan
  artifacts), and verify an OpenCode session.
- `scripts/delete-session.py` with dry-run default and `--execute` gate.
- Delegates log removal to `opencode-session-log-cleanup` and trash-based
  per-file removal to `safe-file-cleanup`.
