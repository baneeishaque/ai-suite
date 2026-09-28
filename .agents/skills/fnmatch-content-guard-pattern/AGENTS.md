# fnmatch Content-Guard Pattern — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes that auto-load
`AGENTS.md` by filename convention. The operational Single Source of Truth lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

Use when you need to safely auto-allow a command whose dangerous argument forms
(such as `system()`, `-f <script>`, `-delete`, `-exec`, `-o <file>`) cannot be
filtered by fnmatch globs alone. This technique applies to any permission system
using last-match-wins pattern ordering with fnmatch.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
algorithm, script reference, worked examples for awk/find/sort, and limitations.
Do NOT execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [`opencode-permission-config`](../opencode-permission-config/SKILL.md) — applies
  this technique to opencode's permission config with concrete pattern additions.
- [`is-this-command-safe`](../is-this-command-safe/SKILL.md) — command safety
  classification SSOT. Determines which commands have dangerous forms.
- [`command-autoapprove-onboarding`](../command-autoapprove-onboarding/SKILL.md) —
  VS Code terminal auto-approve (regex-based, different tool).
