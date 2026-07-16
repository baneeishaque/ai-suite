# OpenCode Config Preserve — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

When setting up OpenCode config preservation in `<private-repo>`,
restoring from a previous migration, or reviewing which opencode files are
tracked and why. Also applies when diagnosing recovery options from `log/`,
`snapshot/`, `storage/session_diff/`, or `tool-output/`.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
directory mapping, gitignore whitelist pattern, and recovery-value
documentation. Do NOT execute any step without first loading `SKILL.md` — this
bridge is intentionally non-actionable.

## Cross-References

- [`tool-config-directory-symlink`](../tool-config-directory-symlink/SKILL.md) — Base skill for the generic migration primitive
- [`opencode-permission-config`](../opencode-permission-config/SKILL.md) — OpenCode permission configuration
- [`vscode-user-settings-symlink`](../vscode-user-settings-symlink/SKILL.md) — Analogous VS Code Insiders config migration
