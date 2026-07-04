---
name: opencode-remote-mcp-setup
description: Composer skill for adding remote MCP servers to OpenCode configuration with authentication and validation.
---

# OpenCode Remote MCP Server Setup Skill

See `.agents/skills/opencode-remote-mcp-setup/SKILL.md` for full documentation.

## When to Use
Use this skill when adding a remote MCP server (HTTP/WebSocket-based) to OpenCode's configuration, such as:
- UptimeRobot MCP server (`https://mcp.uptimerobot.com/mcp`)
- Any other remote MCP server exposing tools over HTTP
- When you need to configure authentication (Bearer token or OAuth) for remote MCP access

## Composition
This skill enriches the `mcp-management` skill with OpenCode-specific knowledge:
- Uses `mcp-management`'s core workflow for server discovery and insertion
- Adds OpenCode-specific schema knowledge (`type: remote` vs `type: local`)
- Provides OpenCode config file locations and JSONC handling
- Includes OpenCode-specific restart requirement and functional test guidance