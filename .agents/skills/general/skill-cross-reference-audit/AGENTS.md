# Skill Cross-Reference Audit — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware agent runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to audit the entire skill library for cross-reference issues: skill names duplicated in both Composition and Related Skills sections, missing AGENTS.md bridge files, missing YAML frontmatter, empty Related Skills sections, or missing Related Skills in skills that have Composition sections.
- You are running the skill-factory Post-Drafting Checklist and need to verify the Composition Audit step.
- You have renamed a skill and need to confirm all references are clean.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the audit scan → report review → fix workflow and all CLI flags (`--skills-dir`, `--json`). Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`skill-factory`](../skill-factory/SKILL.md) — consumer of this audit in §3 Composition Audit
- [`script-template-extraction`](../../script-template-extraction/SKILL.md) — companion base skill for template extraction
- [`script-over-instruction-decomposition`](../../script-over-instruction-decomposition/SKILL.md) — decomposition pattern this skill's audits support
- [`directory-tree-audit`](../directory-tree-audit/SKILL.md) — sibling audit skill for folder depth
