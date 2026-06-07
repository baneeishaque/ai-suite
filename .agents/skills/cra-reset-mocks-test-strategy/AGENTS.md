# CRA resetMocks Test Strategy — Companion Bridge

## Purpose

Companion bridge for non-skill-aware runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- Your Jest+RTL tests fail with `TypeError: ... is not a function` from mocked modules.
- The project uses `react-scripts test` (CRA 5) with the default `resetMocks: true`.
- `jest.fn()` implementations inside `jest.mock` factories silently stop working between tests.
- Mocked hooks return `undefined` instead of configured values.
- Module-level `var` references in `jest.mock` closures capture `undefined` at hoist time.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all solution patterns (§2), the diagnostic
script ([scripts/scan-reset-mocks-vulnerabilities.py](scripts/scan-reset-mocks-vulnerabilities.py)), and the
verification steps (§4). Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-
actionable.

## Cross-References

- [`skill-factory`](../skill-factory/SKILL.md) — Protocol used to create this skill
- [`python-script-generation`](../python-script-generation/SKILL.md) — Script language selection guidance
