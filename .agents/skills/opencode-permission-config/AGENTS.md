# opencode Permission Configuration — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes that auto-load
`AGENTS.md` by filename convention. The operational Single Source of Truth lives in
[`SKILL.md`](SKILL.md).

## When This Skill Applies

Use when the user needs to:

- Configure opencode's `permission.bash` to auto-allow or deny specific commands
- Debug why a permission pattern isn't working (the last-match-wins gotcha)
- Edit `opencode.json` and verify the changes
- Understand the difference between flat actions and pattern-based permission objects

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all
mandates, scripts, and verification steps. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Files & Scripts

| Path | Purpose |
| :--- | :--- |
| `scripts/verify-permission-pattern.py` | Pattern verification script — supports inline JSON, direct opencode.json (JSONC comments), and spec-based regression testing |
| `specs/py-compile-allow.json` | Minimal spec (6 tests) validating `python3 -m py_compile` allow + catch-all ask |
| `specs/full-config.json` | Comprehensive spec (92 tests) validating all patterns in the current opencode.json config — must pass before deploying changes |

## Cross-References

- [`command-autoapprove-onboarding`](../command-autoapprove-onboarding/SKILL.md) —
  VS Code terminal auto-approve (complementary tool-approval domain).
- [`is-this-command-safe`](../is-this-command-safe/SKILL.md) — command safety
  classification before onboarding. This skill's SSOT data source.
- [`vscode-terminal-autoapprove-audit`](../vscode-terminal-autoapprove-audit/SKILL.md) —
  VS Code auto-approve audit (complementary tool-approval domain, different tool).
- [`mcp-cross-tool-config-sync`](../mcp-cross-tool-config-sync/SKILL.md) —
  cross-tool config synchronization patterns.
