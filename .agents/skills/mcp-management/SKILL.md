---
name: mcp-management
description: Industrial protocol for adding, configuring, and verifying MCP servers with cross-tool adaptation.
category: Tool-Infrastructure
---

# MCP Server Management Skill (v1)

This skill provides a standardized protocol for managing MCP (Model Context Protocol) servers within the workspace.
It ensures absolute data fidelity, comprehensive documentation, and secure verification.

***

## 1. Documentation & Discovery

The agent MUST first establish the operational context:

- **Config Location**: The user will provide the target `mcp_config.json` path. If not provided, ask for it.
    - *Example (Antigravity)*: `/Users/[REDACTED]/anti-gravity-mcp_config.json`
- **Target AI Tool**: Identify the tool being configured (e.g., Antigravity, VS Code, Claude Desktop).
- **Source Documentation**: Request official documentation (URLs, `.txt`, `.md`, or `.pdf` files).
    - **URL Handling**: For web links, ALWAYS use the `webfetch` tool to extract detailed technical specifications.

### 1.2 Remote MCP Discovery
- **Transport Identification**: Determine if the MCP server uses stdio (local) or HTTP/WebSocket (remote) transport by checking the documentation for:
  - Local servers: Look for `command` and `args` specifications
  - Remote servers: Look for `url` endpoint and authentication methods (Bearer token, OAuth, etc.)
- **Authentication Method Identification**: Identify supported auth methods from documentation:
  - Bearer Token: Look for `Authorization: Bearer <token>` header pattern
  - OAuth 2.0: Look for `clientId`, `clientSecret`, `tokenUrl`, and `scopes`
  - API Key: Look for custom header patterns like `X-API-Key` or `Authorization: <key>`
- **URL Extraction**: For remote servers, extract the exact WebSocket or HTTP endpoint URL (e.g., `https://mcp.uptimerobot.com/mcp`)

### 1.1 Tool-Specific Adaptation (Extrapolation)

- If the documentation has a dedicated section for the target tool, use it directly.
- If not, research dedicated sections for other tools (e.g., Claude Desktop) to understand the required `command`
  and `args`.
- **Extrapolation**: Adapt instructions from other tools to the target tool's JSON configuration schema.
- **Fail-Safe**: If no tool-specific sections exist, determine the binary path and arguments based on the language
  runtime (Node/Python) or compiled binary status.

***

## 2. Schema & Structure

### 2.1 Dependencies

Before managing MCP servers, the agent MUST verify the following local environment:

- **Runtime Tools**: Verify existence of required runtimes (`node`, `python`, `mise`, `brew`).
- **Absolute Paths**: ALWAYS use absolute paths for the `command` field to ensure execution reliability across
  different shell environments. **Verify the path using `which <tool>` or `find`**.

### 2.2 Security & Configuration

- **Alphabetical Order**: Maintain entries in **alphabetical order** within the `mcpServers` object.
- **Standard Transport**: Default to `stdio` unless specified otherwise.
- **No Hardcoding**: Sensitive keys (API keys, tokens) MUST be managed via environment variables (`env` object)
  or secure secret stores.
- **Naming Convention**: Use uppercase, underscore-separated names for env vars (e.g., `POSTMAN_API_KEY`).

### 2.3 Remote Server Schema

For remote MCP servers (HTTP/WebSocket transport), use the following schema instead of stdio `command`/`args`:

```json
"remote-server-name": {
  "url": "https://mcp.example.com/mcp",
  "headers": {
    "Authorization": "Bearer {env:API_KEY}"
  },
  "oauth": { /* omitted for Bearer token */ },
  "enabled": true
}
```

**Schema Fields**:
- `url` (required): WebSocket or HTTP endpoint URL (e.g., `wss://mcp.example.com/mcp` or `https://mcp.example.com/mcp`)
- `headers` (optional): HTTP headers object, supports env var interpolation like `{env:VAR_NAME}`
  - Commonly used for Authorization: `Bearer {env:API_KEY}` or API keys in custom headers
- `oauth` (optional): OAuth 2.0 configuration object with:
  - `clientId`: string or `{env:OAUTH_CLIENT_ID}`
  - `clientSecret`: string or `{env:OAUTH_CLIENT_SECRET}`
  - `tokenUrl`: string (OAuth token endpoint URL)
  - `scopes`: array of strings (requested permissions)
- `enabled` (optional): boolean, defaults to `true` if omitted
- **Important**: Remote servers MUST NOT include `command` or `args` fields

***

## 3. Integration Workflow

The agent MUST follow different workflows based on server transport type:

### 3.1 Stdio Server Workflow
For servers using standard input/output transport:
1. **Discovery**: Research the server's documentation for required command and arguments.
2. **Path Verification**: Locate the underlying binary using `which` or `find`.
3. **Draft Configuration**: Formulate the JSON entry with `command` (string) and `args` (array) following the patterns in existing config logs.
4. **Insertion**: Insert the entry into the target `mcp_config.json` file in alphabetical order.
5. **Verification**: Execute the verification protocol defined in Section 4.1.

### 3.2 Remote Server Workflow
For servers using HTTP/WebSocket transport:
1. **Discovery**: Research the server's documentation for URL endpoint and authentication methods.
2. **Auth Method Selection**: Determine if server uses Bearer token (API key in headers) or OAuth 2.0.
3. **Credential Gathering**: 
   - For Bearer token: Obtain API key value or environment variable name
   - For OAuth: Obtain client ID, client secret (or env var), token URL, and scopes
4. **Draft Configuration**: Formulate the JSON entry with `url`, `headers` (for Bearer) or `oauth` (for OAuth), and `enabled: true`.
5. **Insertion**: Insert the entry into the target `mcp_config.json` file in alphabetical order within the `mcpServers` object.
6. **Verification**: Execute the verification protocol defined in Section 4.2.

**Note**: The choice between stdio and remote workflows is determined by the server's transport type as documented in its official documentation.

***

## 4. Verification Protocol

The agent MUST verify the new configuration before concluding the task:

### 4.1 Stdio Server Verification Protocol
For servers using standard input/output transport:
1. **JSON Lint**: Run `jq . <config_file>` to ensure the file remains valid after modification.
2. **Command Dry-Run**: Run the `command` with `--help` or a version flag to ensure accessibility.
3. **Functional Pipe Test**: For `stdio` servers, perform a JSON-RPC pipe test:

```bash
# Industrial Pipe Test Sample
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | <command> <args>
```

### 4.2 Remote Server Verification Protocol
For servers using HTTP/WebSocket transport:
1. **JSON Lint**: Run `jq . <config_file>` to ensure the file remains valid after modification.
2. **Restart Required**: Notify user that configuration changes require application restart to take effect.
3. **Functional Test**: After restart, verify server responsiveness with a meaningful query:
   - Example: For UptimeRobot, ask "Show me all monitors" and verify non-empty response
   - General approach: Use a tool/list or similar method to confirm server connectivity
   - Note: No pipe test applicable for HTTP/WebSocket transports

***

## 5. Traceability & Recording

### 5.1 Redaction & Privacy

- **Absolute Paths**: When recording logs, NEVER include biological or system-specific user prefixes.
- **Redaction**: Replace sensitive prefixes (e.g., `/Users/dk/`) with `[REDACTED]`.

### 5.2 Contextual Documentation

- **Session Logs**: Store all session records in the workspace [docs/conversations/](../docs/conversations/) folder.
- **Permanent Link**: Create a relative link in the skill summary or AGENTS.md to the relevant session log for
  future auditability.

***

## 6. Composition by Higher-Level Skills

When the same MCP server entry needs to land in multiple AI tools (VS Code Copilot, JetBrains Copilot,
Copilot CLI, Claude Desktop, Cursor, Windsurf, etc.), do NOT hand-edit each tool's config. Use the
[MCP Cross-Tool Config Sync Skill](../mcp-cross-tool-config-sync/SKILL.md), which:

- Treats this skill's server-entry conventions (§2.2) as the SSOT for individual entries.
- Wraps them in a single canonical `mcp-servers.json`.
- Generates schema-correct per-tool files (`mcpServers` vs `servers`, `tools: ["*"]`, `inputs` passthrough).
- Distributes via symlinks so one canonical edit propagates everywhere.

***

## Related Skills

- [`opencode-remote-mcp-setup`](../opencode-remote-mcp-setup/SKILL.md) — OpenCode-specific composer for remote MCP servers (consumes this skill)
- [`mcp-cross-tool-config-sync`](../mcp-cross-tool-config-sync/SKILL.md) — Cross-tool MCP config sync (consumes this skill)

***

## Design Appendix (Design Fidelity)

| Feature | Change Note | Rationale |
| :--- | :--- | :--- |
| **Path Redaction** | Replaced `/Users/X/` with `/Users/[REDACTED]/`. | Compliance with [redaction\_portability](../redaction-portability/SKILL.md). |
| **Section Restoration** | Re-inserted "Dependencies" and "Integration Workflow". | Restored to ensure full operational guidance is not lost during summarization. |
| **Alphabetical Mandate** | Explicitly required alphabetical ordering in JSON. | Consistency and maintainability in large configuration files. |
| **Functional Pipe Test** | Added bash sample for JSON-RPC pipe verification. | Functional proof-of-work for `stdio` transport. |
| **Config Pathing** | Removed "User Provided Path" label for example. | Improves readability while maintaining privacy. |
