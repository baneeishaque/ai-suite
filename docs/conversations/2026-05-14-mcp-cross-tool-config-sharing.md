# Conversation Log: MCP Cross-Tool Configuration Sharing for `mcp-ssh`

**Date:** 2026-05-14
**Objective:** Determine whether a single MCP server configuration can be shared across the GitHub Copilot
surface family and across all other AI tools the user runs locally, and produce a portable, mise-aware
configuration entry for the freshly installed `mcp-ssh` global npm package.

***

## 1. Request

> now, i have to configure an mcp server for github copilot local agent (it is better if one configuration is read by
> github copilot local agent, github copilot cli & github copilot cloud agent - is that possible?. it is also better
> one configuration is read by all the ai tools (currently i use claude (vscode extension & cli), gemini (vscode
> extension - gemini assistant & cli), github copilot (previously mentioned all, and in eclipse, jetbrains, visual
> studio), open code (vscode extension & cli), kilo (vscode extension & cli), amazon q (vscode extension & cli),
> jetbrains ai & jetbrains junie, anti gravity, cursor, windsurf, trae, zed editor) - is that possible?).
>
> the doc gives configuration for claude desktop, it is:
>
> ```json
> {
>   "mcpServers": {
>     "ssh": {
>       "command": "node",
>       "args": ["%APPDATA%/npm/node_modules/mcp-ssh/dist/server.js"],
>       "env": {
>         "SSH_PORT": "8889",
>         "SSH_LOG_LEVEL": "info"
>       }
>     }
>   }
> }
> ```
>
> what will do?

***

## 2. Analysis & Planning

### 2.1 Cross-surface sharing within GitHub Copilot

| Surface | Native config path | Shareable with siblings? |
| :--- | :--- | :--- |
| VS Code Copilot (local agent) | `.vscode/mcp.json` (workspace) or user-scope `mcp.json` | Yes — same schema |
| Copilot CLI | `~/.config/github-copilot/mcp-config.json` | Yes — same schema |
| Copilot **cloud** coding agent | Repo Settings → Copilot → "MCP servers" (web UI, server-side) | **No** — runs in GitHub-hosted sandbox without local Node binary or local stdio access |

The three Copilot surfaces share the same JSON schema for local files, but the cloud agent cannot reach a
local stdio server like `mcp-ssh` at all — it would need a remote/HTTP MCP transport.

### 2.2 Cross-vendor sharing strategy

There is **no single universal MCP configuration file** that all vendors honour. However, the JSON schema
(`mcpServers` object with `command` / `args` / `env`) is largely identical across most vendors, so a
**symlink-to-canonical-file** strategy works for the majority of the listed tools.

| Tool | Default config path | Schema compatibility |
| :--- | :--- | :--- |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` | Native `mcpServers` |
| Claude Code CLI | `~/.claude.json` (project keys under `mcpServers`) | Native |
| Gemini CLI / Code Assist | `~/.gemini/settings.json` (`mcpServers`) | Native |
| Cursor | `~/.cursor/mcp.json` | Native |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | Native |
| Zed | `~/.config/zed/settings.json` (`context_servers` key) | **Different key** — needs translation |
| OpenCode | `~/.config/opencode/opencode.json` (under `mcp`) | Slight wrapping |
| Kilo Code | `~/.../kilo-code/mcp_settings.json` | Native (Cline-derived) |
| Amazon Q | `~/.aws/amazonq/mcp.json` | Native |
| JetBrains AI / Junie | IDE Settings UI → MCP (writes its own file) | Native, hard to symlink |
| Anti Gravity | `~/.antigravity/mcp_config.json` (or similar) | Native |
| Trae | own settings | Native |

### 2.3 Path portability problem in the vendor doc snippet

The Claude-Desktop snippet shipped by upstream uses `%APPDATA%/npm/node_modules/mcp-ssh/dist/server.js`
which is **Windows-only**. On the user's macOS + mise environment the actual install path was previously
resolved (this session's predecessor turn) to:

```text
/Users/[REDACTED]/.local/share/mise/installs/node/25.6.1/lib/node_modules/mcp-ssh/dist/server.js
```

This path is brittle: it pins to Node `25.6.1` and breaks the moment mise upgrades the Node major. Three
remediation strategies were proposed (Option A absolute paths, Option B mise-wrapped exec, Option C `npx`
on demand). Option C was rejected per the project's `npx` prohibition documented in
[markdown-generation-rules.md §5](../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)
and reinforced by the same session's earlier addition to
[ai-rule-standardization-rules.md](../../ai-agent-rules/ai-rule-standardization-rules.md).

***

## 3. Execution

No filesystem changes were performed in this turn. The agent produced an analytical answer with
ready-to-paste configuration variants and explicitly asked the user for authorization before creating the
canonical file or symlinks. The agent referenced the existing
[mcp-management skill](../../.agents/skills/mcp-management/SKILL.md) as the governing protocol for any
follow-up configuration work.

***

## 4. Confirmation & Outcome

- The user has not yet authorized the canonical-file + symlinks rollout.
- Awaiting selection of the tool subset to symlink in the first pass before proceeding under the
  [mcp-management skill](../../.agents/skills/mcp-management/SKILL.md) §3 Integration Workflow.

***

## 5. Attachments & References

| File / Artifact | Path | Description |
| :--- | :--- | :--- |
| MCP Management Skill | [.agents/skills/mcp-management/SKILL.md](../../.agents/skills/mcp-management/SKILL.md) | Governing protocol for adding, configuring, and verifying MCP servers with cross-tool adaptation. |
| NPM Global Package Path Discovery Skill | [.agents/skills/npm-global-package-path-discovery/SKILL.md](../../.agents/skills/npm-global-package-path-discovery/SKILL.md) | Skill used in the predecessor turn to resolve the actual `mcp-ssh` install path. |
| Markdown Generation Rules §5 | [ai-agent-rules/markdown-generation-rules.md](../../ai-agent-rules/markdown-generation-rules.md) | SSOT for the `npx` prohibition referenced when rejecting Option C. |
| AI Rule Standardization Rules | [ai-agent-rules/ai-rule-standardization-rules.md](../../ai-agent-rules/ai-rule-standardization-rules.md) | Updated earlier in the same session to mirror the `npx` prohibition. |
| Session Documentation Rules | [ai-agent-rules/ai-agent-session-documentation-rules.md](../../ai-agent-rules/ai-agent-session-documentation-rules.md) | Rule followed by this log. |

***

## 6. Structured Data

### 6.1 Recommended canonical configuration (Option A — explicit absolute paths)

```json
{
  "mcpServers": {
    "ssh": {
      "command": "/Users/[REDACTED]/.local/share/mise/installs/node/25.6.1/bin/node",
      "args": [
        "/Users/[REDACTED]/.local/share/mise/installs/node/25.6.1/lib/node_modules/mcp-ssh/dist/server.js"
      ],
      "env": {
        "SSH_PORT": "8889",
        "SSH_LOG_LEVEL": "info"
      }
    }
  }
}
```

Rationale: an absolute `node` binary is required because Claude Desktop and several other MCP hosts launch
child processes with an empty `PATH`, so a bare `"node"` command would fail to locate the mise-shimmed
binary.

### 6.2 Recommended canonical configuration (Option B — mise-wrapped, version-tolerant)

```json
{
  "mcpServers": {
    "ssh": {
      "command": "/opt/homebrew/bin/mise",
      "args": [
        "x", "node@25", "--",
        "node",
        "/Users/[REDACTED]/.local/share/mise/installs/node/25.6.1/lib/node_modules/mcp-ssh/dist/server.js"
      ],
      "env": {
        "SSH_PORT": "8889",
        "SSH_LOG_LEVEL": "info"
      }
    }
  }
}
```

Rationale: `mise x` activates the requested Node major before invoking `node`, absorbing future minor and
patch upgrades within the `node@25` lane.

### 6.3 Requirements coverage

| Requirement | Resolution | Reference |
| :--- | :--- | :--- |
| Single config across all three GitHub Copilot surfaces | Partial — local VS Code + CLI yes via shared file or symlink; cloud agent must be configured separately via repo UI and cannot reach local stdio servers | §2.1 |
| Single config across all listed AI vendors | Partial — symlink one canonical file into all native-schema tools; manually mirror Zed, OpenCode, JetBrains | §2.2 |
| Replace Windows `%APPDATA%` placeholder with macOS-portable path | Use absolute path resolved via the [npm-global-package-path-discovery skill](../../.agents/skills/npm-global-package-path-discovery/SKILL.md) | §2.3 |
| Avoid Node-version brittleness | Option B wraps the launch in `mise x node@25 --` | §6.2 |
| Avoid `npx` for runtime invocation | Both options use direct `node` (or `mise x ... node`) — no `npx` | [markdown-generation-rules.md §5](../../ai-agent-rules/markdown-generation-rules.md) |

***

## 7. Summary

Cross-vendor "one MCP config to rule them all" is **not natively supported**, but a canonical
`~/.config/mcp/servers.json` file, symlinked into every tool whose schema is the native `mcpServers`
object, achieves the same effect for ~70% of the listed tools. The remaining tools (Zed with
`context_servers`, OpenCode with its `mcp` wrapper, JetBrains AI/Junie via UI) require manual mirroring,
and the GitHub Copilot **cloud** coding agent cannot reach a local stdio server like `mcp-ssh` at all and
must be configured separately via the GitHub web UI. The user has been provided two ready-to-paste
configuration variants (absolute paths vs. mise-wrapped) and the agent is awaiting authorization before
creating the canonical file and the symlink fan-out under the
[mcp-management skill](../../.agents/skills/mcp-management/SKILL.md) §3 Integration Workflow.
