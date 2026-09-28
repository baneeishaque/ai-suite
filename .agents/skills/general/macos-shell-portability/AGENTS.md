# macOS Shell Portability — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT resides in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are authoring shell commands or documentation that targets macOS
- You encounter a shell parse error like `; &&` on macOS
- A tool's `--version` flag fails on macOS (BSD vs GNU differences)
- You need to write a cross-platform script that works on both macOS and Linux

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full reference on macOS shell portability, including zsh differences, BSD tool
behavior, and portable command patterns. Do NOT execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete macOS shell portability reference
- [`brew-upgrade-command-assembly`](../../brew-upgrade-command-assembly/SKILL.md) — consumes the `;` vs `&&` pattern
documented here
- [`brew-upgrade-workflow`](../../brew-upgrade-workflow/SKILL.md) — composer that delegates to the assembler
- [`repo-scratch-output-capture`](../../repo-scratch-output-capture/SKILL.md) — alternative output capture approach
(silent redirect to scratch/)
