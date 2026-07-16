# Text File Merge with Overlap Deduplication — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You have two sequential text file parts with duplicated content at the boundary
- You need a single merged file with the overlap automatically removed
- The overlap consists of identical contiguous line sequences
- Domain-agnostic: works on logs, session exports, SQL dumps, CSV, JSONL, any UTF-8 text

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`large-text-file-stream-split`](../large-text-file-stream-split/SKILL.md) — inverse operation (split large file)
- [`near-duplicate-file-comparison`](../near-duplicate-file-comparison/SKILL.md) — forensic comparison with verdict
- [`opencode-session-merge`](../../../oleovista-acers/.agents/skills/opencode-session-merge/SKILL.md) — composer for opencode session exports