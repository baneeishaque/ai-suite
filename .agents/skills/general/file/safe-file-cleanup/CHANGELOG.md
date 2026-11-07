# Changelog

## 2026-08-12 — Initial release

- Base primitive established with trash-aware removal, verification, and
  JSON Lines exit-code contract.
- Composed by `opencode-session-log-cleanup`.

## 2026-11-06 — Preview-verification consumer

- Register optional cleanup from `git-commit-preview-verify`; that consumer owns its macOS fail-closed guard.
  The base cleanup implementation and existing consumers are unchanged.
