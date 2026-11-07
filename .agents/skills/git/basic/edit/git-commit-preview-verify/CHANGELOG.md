# Changelog

## 2026-11-06 — Recoverable optional cleanup

- Delegate optional preview removal to the existing safe-file-cleanup helper.
- Fail closed without macOS Trash, and report cleanup failures with exit 5.
- Keep JSON stdout valid during cleanup and preserve the read-only default report.
- Add fixture-isolated regressions for success, refusal, and helper-failure paths.
