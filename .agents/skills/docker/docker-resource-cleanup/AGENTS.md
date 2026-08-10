# Docker Resource Cleanup — Companion Bridge

## Purpose

This file is the passive bridge for non-skill-aware agent runtimes. The operational SSOT
(the workflow, scope gate, ordered plan, dry-run, exit codes) lives in [`SKILL.md`](SKILL.md).
This bridge only tells you when the skill applies and where to find the procedure.

## When This Skill Applies

Use when the user asks the agent to **delete Docker resources** and you need a controlled,
human-gated, verified cleanup (this composer never mutates without a scope decision):

- "get rid of my docker resources" → `--scope full`.
- "remove stopped containers/images but keep my running services" → `--scope keep-running`.
- "reclaim space from unused images / build cache only" → `--scope unused`.

Do NOT use this skill merely to inspect or count resources — use
[`docker-resource-inventory`](../docker-resource-inventory/SKILL.md) instead.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full workflow, Scope Decision Table, CLI contract, and the
six industrial lessons (L1–L6) the ordering enforces. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [docker-resource-inventory](../docker-resource-inventory/SKILL.md) — base primitive that
  supplies the pre-flight + verification inventories (JSON contract).
- [system-wide-tool-management](../../system-wide-tool-management/SKILL.md) — docker binary
  install/verification when the CLI is absent.
- [repo-scratch-output-capture](../../repo-scratch-output-capture/SKILL.md) — capture long
  dry-run / verification output to `scratch/`.
