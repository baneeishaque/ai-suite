# List Indent Consistency — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT resides in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You edited a markdown file and need to verify that continuation-line indent
  under list items is consistent with sibling items.
- A linter or review flagged indentation drift in a markdown list.
- You are building or invoking a higher-level skill that edits `.md` files
  (skill-factory, markdown-generation, git-atomic-commit-construction).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
script reference, protocol, and output contract. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with script reference, protocol, and output
  contract.
- [`markdown-generation`](../markdown-generation/SKILL.md) — general markdown
  generation with lint auto-fix.
- [`skill-factory` §5.4](../skill-factory/SKILL.md#54-numbered-section-scheme-consistency) —
  mandates indent-continuity check after every skill-doc edit.
