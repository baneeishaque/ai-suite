# MRT Component Test Strategy — Companion Bridge

## Purpose

Companion bridge for non-skill-aware runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are writing or debugging Jest+RTL tests for a component that uses `useMaterialReactTable()` or
`<MaterialReactTable>`.
- The test file does not render an `mrt-table` element or `mockTableOptions` is empty after render.
- You need to verify MRT config props (`enable*`, `manualPagination`, etc.) in unit tests.
- You are hitting errors from `material-react-table/locales/en` import or `useNavigate()` in modal components.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the MRT mock template (§1), assertion patterns
(§2), component dependency isolation (§3), and the boilerplate generator script ([scripts/generate-mrt-test-
boilerplate.py](scripts/generate-mrt-test-boilerplate.py)). Do NOT execute any step without first loading `SKILL.md` —
this bridge is intentionally non-actionable.

## Cross-References

- [`cra-reset-mocks-test-strategy`](../cra-reset-mocks-test-strategy/SKILL.md) — Base skill for CRA `resetMocks: true`
survival (this composer depends on it)
- [`mrt-configuration-debug`](../mrt-configuration-debug/SKILL.md) — Runtime MRT config debugging with playwright-cli
- [`table-persistence-implementation`](../table-persistence-implementation/SKILL.md) — MRT table persistence hook
implementation
