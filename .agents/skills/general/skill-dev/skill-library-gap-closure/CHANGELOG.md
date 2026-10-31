# Skill Library Gap Closure — Changelog

| Date | Version | Change |
| :--- | :--- | :--- |
| 2026-10-17 | v1.0.0 | Initial release: the evidence-driven gap-closure workflow from session analysis to a ranked gap register to routed closure under a plan-first gate. |
| 2026-10-20 | v1.1.0 | Added automatic session-evidence acquisition and path-attribution indexing through the new Tier-1 driver; gap registers and plans now carry an Evidence Verification Index. |
| 2026-10-27 | v1.2.0 | Added mandatory session verification via `--verify-text` and the `opencode-current-session-id` finder; the driver fails closed on no match or ambiguity and records `session_verification` in the evidence manifest. |
| 2026-10-30 | v1.3.0 | Plans now require an absolute Files-to-Touch section, so approval cannot proceed without naming every file the plan will change. |
| 2026-10-31 | v1.4.0 | Added the deliberate evidence re-run recipe (§2.6.1): new purpose suffix, separate evidence directory, pre-created redirect target, session re-verification, and retention of the prior report/manifest. |
