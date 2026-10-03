# Changelog

| Date | Version | Summary | Rationale |
| :--- | :--- | :--- | :--- |
| 2026-09-27 | v1 | Initial release — `scripts/replace-and-replay.py` (prepare/finish/verify) for deterministic in-place single-commit replacement with range-diff parity verification (full marker accounting; at most one changed commit). | Extracted as a base primitive from the proven in-place route: no sequence editor, no todo writer, no interactive stop. Composer Mode B delegates here. |
