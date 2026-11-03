# Changelog — opencode-session-deletion

## [1.0.1] - 2026-11-04

- Add the mandatory gap-closure gate: deletion is blocked until
  `skill-library-gap-closure` reports zero open gaps for the target session.
- `--execute` now requires `--gap-closure-cleared`; otherwise exits `2`.

## [1.0.0] - 2026-11-04

- Initial composer: discover, confirm, delete (DB + logs + scratch + plan
  artifacts), and verify an OpenCode session.
- `scripts/delete-session.py` with dry-run default and `--execute` gate.
- Delegates log removal to `opencode-session-log-cleanup` and trash-based
  per-file removal to `safe-file-cleanup`.
