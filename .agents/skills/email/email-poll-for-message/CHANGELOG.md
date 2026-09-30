# Changelog

## [1.0.0] - 2026-09-30

### Added

- Initial release of the `email-poll-for-message` composite skill.
- `scripts/search-messages.py` — one-shot IMAP search check command with
  subject/from/unseen/since filters, read-only access, encoded-header decoding,
  and an offline `--source-file` fixture mode.
- `scripts/poll-email-message.py` — composite driver over `poll-until` with
  environment-variable-only credentials.
- `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`.
- Registered under the new `email/` domain in the domain taxonomy.
