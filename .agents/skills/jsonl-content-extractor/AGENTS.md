# JSONL Content Extractor — Companion Bridge

## Purpose

This is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to extract specific content blocks from a JSONL file where each line contains
  structured data with nested arrays of typed items.
- You need to split content into matched and unmatched sets based on type/value filters at specific path levels.
- You are building a composer that processes AI session logs, audit trails, or any JSONL-serialized event stream.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the CLI contract,
navigation logic, output schema, and all mandates. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

  this base primitive for Claude session export
- [`skill-factory`](../skill-factory/SKILL.md) — §2.0 Layering Decision, §2.2 SKILL.md Composition, §3 Post-Drafting Checklist
