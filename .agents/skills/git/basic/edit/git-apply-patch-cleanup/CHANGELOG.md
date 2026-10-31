# Changelog

| Date | Version | Summary | Rationale |
| :--- | :--- | :--- | :--- |
| 2026-06-29 | v1.0.0 | Initial release — `scripts/apply-patch` applies a git patch with `--check`, `--stat`/`--dry-run`, and optional cleanup. | Extracted from a completed session workflow into a domain-agnostic base primitive. |
| 2026-10-31 | v1.1.0 | Added `scripts/check-patch-coexistence.py` — layered patch preflight across line, content, knowledge, and structure dimensions; cleanup now prefers the system trash. | Prevents the silent layering failure where a candidate patch applies cleanly but collides with an already-applied pre-state patch. |
