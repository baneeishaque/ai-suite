# opencode-session-deletion-plan — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes that
auto-load `AGENTS.md` by filename convention. The operational SSOT lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to plan the deletion of an OpenCode session from a session other
  than the one being deleted.
- The target session's work must survive the deletion as verifiable content
  markers, a commit roster, and a gap-closure verdict.
- An existing deletion plan needs to be rendered or re-rendered from a JSON
  spec.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full composition rationale, spec
contract, protocol, and edge cases. Do NOT execute any step without first
loading `SKILL.md`.

The deterministic step is always the generator:

```bash
python3 scripts/build-deletion-plan.py --spec <spec.json>
```

Never hand-assemble the plan when the generator can render it, and never
run the deletion composer from this skill — planning and execution are
deliberately separate.

## Local Contracts

- `markers` and `markers_none: true` are mutually exclusive; one is required.
- Every marker carries an absolute path, a literal pattern, and a match mode.
- The rendered plan embeds the gap-closure gate and the plan's own
  retirement step.
- The generator refuses to overwrite without `--overwrite`; bump `--version`
  for a new plan version.
- The plan is local-only; it may contain session IDs and absolute paths.

## Cross-References

- [`opencode-session-deletion`](../opencode-session-deletion/SKILL.md) —
  executes the rendered plan.
- [`opencode-session-analysis-bundle`](../opencode-session-analysis-bundle/SKILL.md) —
  produces the transcript evidence used to choose markers.
- [`planning-artifact-naming`](../../../general/planning/planning-artifact-naming/SKILL.md) —
  the plan filename contract.
- [`planning-artifact-lifecycle`](../../../general/planning/planning-artifact-lifecycle/SKILL.md) —
  the plan-first gate and retirement-last rule.
- [`markdown-lint-workflow`](../../../general/markdown-lint-workflow/SKILL.md) —
  the lint gate for the rendered plan.

## Verification

- `python3 scripts/build-deletion-plan.py --help`
- A spec with neither `markers` nor `markers_none` exits `1`.
- A rendered plan passes `markdownlint-cli2` with zero issues.
