# Markdown Section to Companion Doc — Companion Bridge

## Purpose

This file is the passive bridge for non-skill-aware agent runtimes. The operational SSOT (CLI contract,
exit codes, output semantics) lives in [`SKILL.md`](SKILL.md). This bridge only tells you when the skill
applies and where to find the procedure.

## When This Skill Applies

Use when you need to relocate a named `## Section` of any markdown document into a sibling companion file:

- A document has grown a long metadata or record section (`Changelog`, `Traceability`, appendices) that
  should live in its own file while the source keeps a pointer.
- You want to audit whether sections are inline (body content) or external (pointer-only) — `--check`.
- You want an idempotent, byte-preserving split — re-running on an already-split doc is a no-op.

Do NOT use this skill for content-rewriting, re-indenting, or reformatting — that is the territory of
other text-manipulation primitives.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and
verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [skill-doc-metadata-separation](../skill-doc-metadata-separation/SKILL.md) — composer that applies this
  primitive to skill metadata sections.
- [skill-factory](../../skill-factory/SKILL.md) — §2.2.1 script authoring mandates and §3 post-drafting
  checklist governing how this skill's scripts were authored.
