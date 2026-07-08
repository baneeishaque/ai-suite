---
name: script-over-instruction-decomposition
description: When designing or refactoring a rule, skill, or sub-agent prompt, decompose its procedure into a deterministic script tier and a prose tier — encode every deterministic step as an executable script under scripts/, leave only judgement/branching/gates in prose.
category: Rule-Management
---

# Script Over Instruction Decomposition

This skill is fully documented in [`SKILL.md`](SKILL.md).

## Trigger

Activate this skill whenever:

- Designing a NEW rule or skill that contains multi-step mechanical
  work.
- Refactoring an EXISTING rule/skill whose prose contains a long
  bash recipe.
- Reviewing an agent prompt that hand-codes a deterministic procedure.

## The Determinism Hierarchy

| Tier | Encoding | Choose when |
|---|---|---|
| A | Script under `scripts/` | Deterministic mechanical work |
| B | Prose invocation `python3 scripts/foo.py` | Threading the script into the agent's flow |
| C | Pure prose | Judgement, branching, gates, explanations |

See [`SKILL.md`](SKILL.md) for the full decomposition procedure and
mandatory/appropriate-tier categories.
