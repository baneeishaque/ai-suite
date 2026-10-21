# Skill Library Gap Closure — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational
SSOT lives in [`SKILL.md`](SKILL.md). It also acquires the session transcripts,
full-fidelity JSONL, workflow report, and path-attribution evidence automatically, so the
register and plan are verifiable without a second prompt.

## When This Skill Applies

- A real workflow was executed and you need to know whether the skill library already
  documents it, and what to add if not.
- You have evidence of undocumented practice (a workflow-analysis report, a walkthrough)
  and must turn it into a ranked, evidence-backed gap register.
- You are choosing between enriching an existing skill and creating a new one, and want
  the choice made by rule rather than by preference.
- You have a session ID and need the human transcripts, machine JSONL, report skeleton,
  and path evidence generated as part of the closure pass.
- You need to verify a gap register or plan claim against the exact session turn and tool
  call that produced it.

For the narrower rule-file migration path (turn a redundant RULE into a skill), use
[`rule-to-skill-industrialization`](../../../rule-to-skill-industrialization/SKILL.md) — this
skill is for session-derived evidence.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the verdict
vocabulary, the new-versus-enrich decision, and the plan-first approval gate. Do NOT
execute any step without first loading `SKILL.md` — this bridge is intentionally
non-actionable. For session-backed evidence, run `scripts/run-gap-closure-evidence.py`
before extracting gaps; use `--attribution-only --paths-file` once candidate gaps
exist.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the gap-closure workflow.
- [`skill-factory`](../../../skill-factory/SKILL.md) — owns the authoring flows this skill
  routes into.
- [`rule-to-skill-industrialization`](../../../rule-to-skill-industrialization/SKILL.md) —
  sibling protocol for rule-file input.
- [`opencode-session-analysis-bundle`](../../../opencode/session/opencode-session-analysis-bundle/SKILL.md)
  — produces the human transcripts, machine JSONL, report skeleton, and manifest this skill
  consumes.
- [`opencode-session-path-attribution`](../../../opencode/opencode-session-path-attribution/SKILL.md)
  — maps each cited path token to the session turn and tool call that touched it.
