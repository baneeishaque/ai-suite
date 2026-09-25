# Changelog

## [1.0.0] - 2026-09-25

### Added

- Initial release of the `pr-merge-decision-classifier` skill
- Classifier core `scripts/classify-pr.py` — read-only state builder via `gh`, four
  backends (`laya`, `apimaster`, `morphllm`, `typesafe`, plus `all` unanimity mode),
  stricter gate defaults (confidence ≥ 0.9, risk ≤ 0.5), optional `--execute` auto-merge,
  and the verdict output contract
- Local server manager `scripts/laya-server.bash` — `start` / `stop` / `restart` /
  `status` / `health`, default `127.0.0.1:8081`, PID/log under `${TMPDIR:-/tmp}`
- Six fixtures (5 canned-answer fixtures + `state-sample.json`) driving
  `--self-test` (`SELF-TEST: PASS (5/5)`)
- `SKILL.md`, `AGENTS.md` (companion bridge), `TRACEABILITY.md`
