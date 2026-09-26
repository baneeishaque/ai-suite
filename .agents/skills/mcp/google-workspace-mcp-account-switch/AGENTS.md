# Google Workspace MCP Account Switch — Companion Bridge

## Purpose

This file is the passive bridge for non-skill-aware agent runtimes. The operational SSOT
(the two-call protocol, ordering constraint, edge cases) lives in [`SKILL.md`](SKILL.md).
This bridge only tells you when the skill applies and where to find the procedure.

## When This Skill Applies

Use when the **active google-workspace MCP account must change** before an operation:

- A Gmail search/read or calendar operation must run under a different identity.
- The user asks to "switch to my other Google account" for MCP tools.
- A composer's account preflight found a mismatch between the active identity and the target
  mail/calendar.

Do NOT use this skill to configure the MCP server itself (use
[`mcp-management`](../../mcp-management/SKILL.md)) or to manage REST/PKCE credentials (use
[`google-oauth-setup`](../../google-oauth-setup/SKILL.md)).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the exact two-call sequence (`auth_clear` → dependent
`people_getMe`), the never-batch constraint, and the edge cases. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [mcp-management](../../mcp-management/SKILL.md) — server add/configure/verify lifecycle.
- [google-oauth-setup](../../google-oauth-setup/SKILL.md) — REST/PKCE credential layer.
