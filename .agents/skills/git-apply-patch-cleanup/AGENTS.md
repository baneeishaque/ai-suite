# git-apply-patch-cleanup — Companion Bridge

## Purpose

This file is a bridge for non-skill-aware agent runtimes (Codex CLI,
some Cursor profiles, Continue.dev) that auto-load `AGENTS.md` by
filename convention but do not parse `agentskills.io` YAML frontmatter
or the `.agents/skills/<name>/SKILL.md` directory contract. It ensures
those agents discover this skill exists and know to read `SKILL.md`
for the operational details.

## When This Skill Applies

- You have a unified-diff patch file (`.patch`, `.diff`) to apply to the current git repository
- You want verification before application (`git apply --check`)
- You optionally want the patch file deleted after successful application (`--cleanup`)
- You need a dry-run / stat preview without modifying the working tree (`--stat`, `--dry-run`)

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure,
including all mandates, scripts, and verification steps. Do NOT
execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  — commits applied changes atomically
- [`git-submodule-selective-init-no-lfs`](../git-submodule-selective-init-no-lfs/SKILL.md)
  — base primitive for submodule init
- [Scripting Language Selection Rules](../../../ai-agent-rules/scripting-language-selection-rules.md)
  — tier justification for Bash script
