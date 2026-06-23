# Script Template Extraction — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware agent runtimes. The operational Single Source of Truth (SSOT) lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- A Python script in a skill's `scripts/` directory contains multi-line string constants that represent file content (YAML templates, markdown, .gitignore stanzas, config blocks). The extraction script scans the AST for `TEMPLATE = """..."""` patterns and automatically separates the content into a `.template` file while rewriting the script to read from it at runtime.
- You need to extract embedded template content into standalone `.template` files while automatically rewriting the script to read from the template at runtime. The script handles both single files and recursive directory traversal, supports dry-run preview, and creates `.bak` backups before modifying scripts.
- You are running the skill-factory Post-Drafting Checklist (§3) and the Composition Audit step flags an embedded-template violation. Run this skill's script to automate the remediation.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the scan → extract → rewrite → verify workflow and all CLI flags (`--dry-run`, `--force`, `--recursive`). Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`skill-factory`](../skill-factory/SKILL.md) — defines the Template Extraction Mandate (§2.2.1.1.6) and consumes this skill in the Post-Drafting Checklist
- [`script-over-instruction-decomposition`](../script-over-instruction-decomposition/SKILL.md) — the decomposition pattern this skill complements (templates vs. script logic is a sibling separation to scripts vs. prose)
- [`skill-cross-reference-audit`](../general/skill-cross-reference-audit/SKILL.md) — automated audit for skill graph issues; run after extraction to verify the skill graph is clean
- [`python-script-generation`](../python-script-generation/SKILL.md) — standards for Python scripts that this skill modifies
