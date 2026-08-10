# Skill Doc Metadata Separation — Companion Bridge

## Purpose

This file is the passive bridge for non-skill-aware agent runtimes. The operational SSOT (when to apply,
workflow, CLI contract, exit codes) lives in [`SKILL.md`](SKILL.md). This bridge only tells you when the
skill applies and where to find the procedure.

## When This Skill Applies

Use when a skill's `SKILL.md` carries metadata sections (`Changelog`, `Traceability`) that are
information rather than instructions, and should live in sibling companion files (`CHANGELOG.md`,
`TRACEABILITY.md`):

- A single skill's `SKILL.md` has grown long with changelog or provenance content.
- You want a library-wide audit of which skills still carry inline metadata sections.
- You want an idempotent, byte-preserving split with a mandatory human judgement gate between plan
  (`--dry-run`) and execution (`--split`).

Do NOT use this skill for instruction-content reorganization or general markdown editing.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and
verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [markdown-section-to-companion-doc](../markdown-section-to-companion-doc/SKILL.md) — base primitive
  that performs the actual section extraction.
- [skill-factory](../../skill-factory/SKILL.md) — §2.1 directory layout and §2.2 SKILL.md composition
  governing the convention this skill enforces.
