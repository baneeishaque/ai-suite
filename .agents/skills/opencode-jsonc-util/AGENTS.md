# OpenCode JSONC Utility — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to read or validate an OpenCode config file (`opencode.json`,
  `opencode.jsonc`) that contains `//` comments and/or trailing commas.
- A higher-level skill or script needs strict JSON out of an OpenCode JSONC
  config via the stable `read-jsonc.py <file>` contract.

Do NOT use this skill for non-OpenCode JSONC files — use the
[`jsonc-cst-util`](../json/jsonc-cst-util/SKILL.md) base primitive directly.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the
CLI/API contract, protocol, and downstream composition table. Do NOT execute
any step without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete procedure.
- [`jsonc-cst-util`](../json/jsonc-cst-util/SKILL.md) — base primitive that
  performs the CST parse.
- [`opencode-remote-mcp-setup`](../opencode-remote-mcp-setup/SKILL.md) —
  consumer for MCP config validation.
- [`opencode-permission-config`](../opencode-permission-config/SKILL.md) —
  consumer for permission-pattern verification.
