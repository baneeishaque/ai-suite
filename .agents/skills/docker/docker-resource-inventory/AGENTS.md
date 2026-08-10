# Docker Resource Inventory — Companion Bridge

## Purpose

This file is the passive bridge for non-skill-aware agent runtimes. The operational SSOT
(CLI contract, exit codes, JSON output anatomy) lives in [`SKILL.md`](SKILL.md). This bridge
only tells you when the skill applies and where to find the procedure.

## When This Skill Applies

Use whenever the agent must **enumerate Docker resources** before deciding or acting (this
skill is read-only — it never mutates Docker state):

- Pre-flight of any destructive Docker operation ("what exists before I delete anything?").
- Post-action verification ("is the daemon actually empty / reduced?").
- Disk-usage triage (`docker system df` breakdown, reclaimable bytes).
- Detecting running vs. stopped containers or dangling volumes.

Do NOT use this skill when the goal is to **delete** resources — use
[`docker-resource-cleanup`](../docker-resource-cleanup/SKILL.md) instead.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the JSON contract,
exit codes, and manual usage examples. Do NOT execute any step without first loading
`SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [docker-resource-cleanup](../docker-resource-cleanup/SKILL.md) — composer that consumes this
  inventory (pre-flight report + post-cleanup verification) via `--format json`.
- [system-wide-tool-management](../../system-wide-tool-management/SKILL.md) — install/verify the
  docker CLI when the binary is absent.
- [repo-scratch-output-capture](../../repo-scratch-output-capture/SKILL.md) — capture long
  inventory output to `scratch/` when probing a remote host.
