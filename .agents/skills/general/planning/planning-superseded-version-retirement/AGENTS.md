# Superseded Version Retirement — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

- A user asks to remove / retire / "get rid of" an OLD version of a versioned planning artifact (implementation-plan,
task, commit-preview) while a newer version survives.
- Cleaning up stale "vN is kept intact / left untouched / History mandate" references in the surviving version and
task.md after a prior retirement.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full gated protocol. Abbreviated for bridge context:

1. **Coverage gate** — run `scripts/audit-version-coverage.py --old <vN> --new <vN+1> --json` (sibling base skill).
Abort unless verdict is `FULL`.
2. **Authorization gate** — show the `--dry-run` plan; obtain explicit user consent before any mutation.
3. **Execute** — `python3 scripts/retire-superseded-version.py --old <vN> --new <vN+1> --confirm DELETE` (trash only;
never `rm`).
4. **Rebase + verify** — re-point stale references in the surviving doc and task.md per the SKILL.md procedure, then
`--verify` (exit 0 = zero STALE refs).

Do NOT re-derive the audit or sweep logic ad-hoc — this bridge is intentionally non-actionable.

## Cross-References

- [`planning-version-coverage-audit`](../planning-version-coverage-audit/SKILL.md) — consumed coverage gate.
- [`planning-artifact-lifecycle`](../planning-artifact-lifecycle/SKILL.md) — lifecycle defaults for deletion/retention.
- [`planning-artifact-naming`](../planning-artifact-naming/SKILL.md) — naming of the versioned artifacts.
