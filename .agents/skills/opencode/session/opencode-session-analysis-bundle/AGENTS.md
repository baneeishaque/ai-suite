# Opencode Session Analysis Bundle — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are asked to analyse AND transcribe an opencode logger session in one run, rather than performing
  either half on its own.
- You need per-turn YAML transcripts placed next to the source logs (`ses_<id>/transcripts/`) together
  with a scratch analysis report, a full-fidelity JSONL, and an absolute-path manifest.
- You need turn exclusions recorded deterministically, with struck turns, rationale, and repaired counts
  in the report while source logs and transcripts stay untouched.
- You are building a higher-level workflow that consumes session transcripts plus a workflow reconstruction
  and want the whole bundle produced by a single driver invocation.
- You need session discovery with pending-marker verification instead of a remembered session ID.
- You want one CLI surface guaranteeing discovery → locate → transcribe → report → manifest ordering
  instead of re-deriving the sequence ad hoc.
- You need the reverse path back: from a bundle transcript file to the durable source log that produced it.
- You want the full-fidelity JSONL persisted beside the scratch report for later machine analysis.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts,
and verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) - SSOT with composition rationale, operational logic, and driver contract.
- [`opencode-session-problem-solution-workflow-analysis`](../../opencode-session-problem-solution-workflow-analysis/SKILL.md)
  composer whose skeleton this bundle fills with judgement sections.
- [`opencode-session-yaml-conversation-extractor`](../../opencode-session-yaml-conversation-extractor/SKILL.md)
  base producing the adjacent per-turn transcripts.
- [`opencode-session-yaml-transcript-extractor`](../../opencode-session-yaml-transcript-extractor/SKILL.md)
  base producing the full-fidelity JSONL beside the scratch report.
- [`opencode-session-transcript-to-source-resolve`](../../opencode-session-transcript-to-source-resolve/SKILL.md)
  reverse navigator from bundle transcripts back to source logs.
