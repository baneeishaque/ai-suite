---
name: session-audit-commit-arrangement
description: Batch 1 commit preview — OpenCode Infrastructure Layer (Commits 1-4)
artifact-type: commit-preview
version: 2
---

# Session Audit Commit Arrangement — Batch 1 Preview (v2)

**Session**: `ses_0dd374af6ffe02JHq06EQ89B48`
**Date**: 2026-07-04
**Phase**: Batch 1 of 4 — OpenCode Infrastructure Layer
**Commits**: C1–C4

---

## Batch 1 Overview

| # | Message | New files | Modified tracked | AGENTS.md rows | Total Δ |
|:---|:---|:---|---:|:---:|:---:|
| C1 | `feat(skill): add opencode-jsonc-util base skill` | 3 files (127 lines) | 3 files (+1 each) | +1 (JSONC Util) | +130 |
| C2 | `feat(skill): add opencode-remote-mcp-setup skill` | 3 files (377 lines) | 0 | +1 (Remote MCP) | +378 |
| C3 | `feat(mcp): add remote MCP support and OpenCode generators` | 1 file (112 lines) | 3 files (+160/-17) | 0 | +255 |
| C4 | `feat(skill): add opencode-permission-config skill` | 6 files (906 lines) | 0 | 0 (exists) | +906 |

---

## C1: feat(skill): add opencode-jsonc-util base skill

### Files

**New (untracked):**
- `.agents/skills/opencode-jsonc-util/AGENTS.md` — 18 lines
- `.agents/skills/opencode-jsonc-util/SKILL.md` — 45 lines
- `.agents/skills/opencode-jsonc-util/scripts/read-jsonc.py` — 64 lines

**Modified (tracked):**
- `.agents/skills/opencode-config-preserve/SKILL.md` — +1 line
- `.agents/skills/opencode-google-gemini-config/SKILL.md` — +1 line
- `.agents/skills/opencode-provider-persistence-config/SKILL.md` — +1 line
- `AGENTS.md` — +1 row (Hunk 5, row 1 of 8)

### Hunks

#### opencode-config-preserve/SKILL.md — Section 6 Related Skills
```diff
 ## 6. Related Skills
 
+- [`opencode-jsonc-util`](../opencode-jsonc-util/SKILL.md) — Base JSONC utility for OpenCode config files
 - [`tool-config-directory-symlink`](../tool-config-directory-symlink/SKILL.md)
```

#### opencode-google-gemini-config/SKILL.md — Section 5 Related Skills
```diff
 ## 5. Related Skills
 
+- [`opencode-jsonc-util`](../opencode-jsonc-util/SKILL.md) — Base JSONC utility for OpenCode config files
 - [`opencode-provider-persistence-config`](../opencode-provider-persistence-config/SKILL.md)
```

#### opencode-provider-persistence-config/SKILL.md — Related Skills
```diff
 ## Related Skills
 
+- [`opencode-jsonc-util`](../opencode-jsonc-util/SKILL.md) — Base JSONC utility for OpenCode config files
 - [`opencode-google-gemini-config`](../opencode-google-gemini-config/SKILL.md)
```

#### AGENTS.md — Hunk 5 (row 1 of 8)
```diff
+| OpenCode JSONC Util | [`.agents/skills/opencode-jsonc-util/SKILL.md`](.agents/skills/opencode-jsonc-util/SKILL.md) | Base — read and validate OpenCode JSONC config files (strip `//` comments, trailing commas); consumed by opencode-remote-mcp-setup and opencode-permission-config. |
```

### New File Content

#### opencode-jsonc-util/AGENTS.md (18 lines)
```markdown
---
name: opencode-jsonc-util
description: Base — read and validate OpenCode JSONC config files (strip `//` comments, trailing commas).
---

# OpenCode JSONC Utility

See `.agents/skills/opencode-jsonc-util/SKILL.md` for full documentation.

## When to Use

Use this skill when reading, validating, or transforming OpenCode JSONC configuration files — especially when
consumed by higher-level skills that need to parse `opencode.json` or `opencode.jsonc`.

## Related

- [`opencode-remote-mcp-setup`](../opencode-remote-mcp-setup/SKILL.md)
- [`opencode-permission-config`](../opencode-permission-config/SKILL.md)
```

#### opencode-jsonc-util/SKILL.md (45 lines)
```markdown
---
name: opencode-jsonc-util
description: Base — read and validate OpenCode JSONC config files (strip `//` comments, trailing commas); consumed by opencode-remote-mcp-setup and opencode-permission-config.
category: Base-Utility
---

# OpenCode JSONC Utility Skill

Base primitive for reading and validating OpenCode's JSONC configuration format — files that permit `//`
comments and trailing commas, which standard `json.loads` rejects.

## JSONC Format Summary

OpenCode config files (`opencode.json`, `opencode.jsonc`) extend JSON with two relaxations:

1. **Trailing commas** are permitted before `]` and `}`.
2. **`//` comments** are permitted as full-line or inline (trailing) comments.

## Usage

### CLI

```bash
python3 scripts/read-jsonc.py <file-path>
```
- Reads the file, strips `//` comment lines and trailing commas, outputs valid JSON to stdout.
- Exit 0 on success, 1 on failure with diagnostic to stderr.

### Python

Import `read_jsonc` from `scripts/read-jsonc.py`:
```python
from read_jsonc import read_jsonc
data = read_jsonc("/path/to/opencode.json")
```

## Related Skills

- [`opencode-remote-mcp-setup`](../opencode-remote-mcp-setup/SKILL.md) — Consumes this skill for JSONC reading
- [`opencode-permission-config`](../opencode-permission-config/SKILL.md) — Consumes this skill for JSONC reading
- [`opencode-provider-persistence-config`](../opencode-provider-persistence-config/SKILL.md) — OpenCode credential storage details
- [`opencode-google-gemini-config`](../opencode-google-gemini-config/SKILL.md) — Gemini provider configuration
- [`opencode-config-preserve`](../opencode-config-preserve/SKILL.md) — OpenCode config preservation
```

#### opencode-jsonc-util/scripts/read-jsonc.py (64 lines)
```python
#!/usr/bin/env python3
\"\"\"Read a JSONC file (JSON with // comments and trailing commas) and print valid JSON to stdout.

Usage:
    python3 scripts/read-jsonc.py <file-path>

Exits 0 on success, 1 on failure.
\"\"\"

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def read_jsonc(file_path: str) -> dict:
    \"\"\"Read a JSONC file, strip comments and trailing commas, return parsed dict.\"\"\"
    text = Path(file_path).read_text(encoding="utf-8")

    lines = text.split("\\n")
    stripped: list[str] = []
    for line in lines:
        if "//" in line:
            in_string = False
            for i, ch in enumerate(line):
                if ch == '"':
                    in_string = not in_string
                elif ch == "/" and i + 1 < len(line) and line[i + 1] == "/" and not in_string:
                    line = line[:i]
                    break
        stripped.append(line)

    cleaned = "\\n".join(stripped)
    cleaned = re.sub(r",(\\s*[\\]\\}])", r"\\1", cleaned)

    return json.loads(cleaned)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file-path>", file=sys.stderr)
        return 1

    try:
        data = read_jsonc(sys.argv[1])
    except FileNotFoundError:
        print(f"ERROR: file not found: {sys.argv[1]}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSONC: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Deferred Forward References
None — all cross-referenced skills (opencode-remote-mcp-setup, opencode-permission-config, etc.) are either committed in same batch or exist in HEAD.

---

## C2: feat(skill): add opencode-remote-mcp-setup skill

### Files

**New (untracked):**
- `.agents/skills/opencode-remote-mcp-setup/AGENTS.md` — 21 lines
- `.agents/skills/opencode-remote-mcp-setup/SKILL.md` — 156 lines
- `.agents/skills/opencode-remote-mcp-setup/scripts/validate-opencode-mcp.py` — 200 lines

**Modified (tracked):**
- `AGENTS.md` — +1 row (Hunk 5, row 2 of 8)

### Hunks

#### AGENTS.md — Hunk 5 (row 2 of 8)
```diff
+| OpenCode Remote MCP Setup | [`.agents/skills/opencode-remote-mcp-setup/SKILL.md`](.agents/skills/opencode-remote-mcp-setup/SKILL.md) | Composer skill for adding remote MCP servers to OpenCode configuration with authentication and validation. |
```

### New File Content

#### opencode-remote-mcp-setup/AGENTS.md (21 lines)
```markdown
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
```

#### opencode-remote-mcp-setup/SKILL.md (156 lines)
```markdown
---
name: opencode-remote-mcp-setup
description: Composer skill for adding remote MCP servers to OpenCode configuration with authentication and validation.
category: Tool-Infrastructure
---

# OpenCode Remote MCP Server Setup Skill (v1)

This skill provides a standardized procedure for adding remote MCP servers (like UptimeRobot) to OpenCode's configuration.
It enriches the generic MCP management procedure with OpenCode-specific schema knowledge and validation.

***

## 1. Prerequisites

Before adding a remote MCP server, the agent MUST:

- **Verify opencode installation**: Check that `opencode` command is available in PATH
- **Determine config scope**: Ask user whether to modify global (`~/.config/opencode/opencode.json`) or project (`./opencode.json`) config
- **Research server documentation**: Use `webfetch` to retrieve official MCP server documentation for URL and auth methods

## 2. Configuration Schema

### 2.1 Local vs Remote Servers
OpenCode's `mcp` section supports two server types:

**Local (stdio) servers**:
```json
"mcp": {
  "local-server-name": {
    "type": "local",
    "command": "/path/to/binary",
    "args": ["--flag", "value"],
    "env": {
      "API_KEY": "{env:REAL_API_KEY}"
    },
    "enabled": true
  }
}
```

**Remote (HTTP) servers**:
```json
"mcp": {
  "remote-server-name": {
    "type": "remote",
    "url": "https://mcp.example.com/mcp",
    "headers": {
      "Authorization": "Bearer {env:API_KEY}"
    },
    "enabled": true
  }
}
```

### 2.2 Authentication Methods
OpenCode remote MCP servers support:

1. **Bearer Token (recommended for simplicity)**:
   - `headers.Authorization`: `Bearer <token>` or `Bearer {env:ENV_VAR_NAME}`
   - Token can be literal or interpolated from environment variable

2. **OAuth 2.0**:
   - `oauth` object with:
     - `clientId`: string or `{env:OAUTH_CLIENT_ID}`
     - `clientSecret`: string or `{env:OAUTH_CLIENT_SECRET}`
     - `tokenUrl`: string (OAuth token endpoint URL)
     - `scopes`: array of strings (requested permissions)

## 3. Integration Workflow

### 3.1 Discovery Phase
1. Use `webfetch` to retrieve MCP server documentation
2. Identify the server's URL endpoint
3. Determine available authentication methods

### 3.2 Auth Method Selection
Ask the user to choose authentication method:
- API Key/Bearer token (simplest, recommended)
- OAuth 2.0 (more complex)

### 3.3 Credential Collection
Based on selected auth method:
- **Bearer token**: Ask for API key value or environment variable name
- **OAuth**: Ask for client ID, client secret, token URL, and scopes

### 3.4 Config Scope Selection
Ask user: "Modify global config (`~/.config/opencode/opencode.json`) or project config (`./opencode.json`)?"

### 3.5 Configuration Insertion
1. Read the target `opencode.json` file (handle JSONC format)
2. Locate or create the `mcp` object
3. Add server entry with appropriate fields
4. Maintain alphabetical order within the `mcp` object
5. Write back to file preserving JSONC format

### 3.6 Validation
1. Validate JSON syntax: `jq empty <config_file>`
2. Verify config structure: `jq '.mcp.<server-name>' <config_file>`
3. Confirm required fields are present and correctly formatted

### 3.7 Post-Installation Steps
1. Instruct user to restart opencode client
2. Recommend functional test

## 4. Verification Protocol

1. **JSON Lint Check**: `jq empty <config_file>` — must exit 0
2. **Config Read-Back**: `jq '.mcp.<server-name>' <config_file>` — must return object
3. **Restart Notification**: Inform user to restart opencode
4. **Functional Test Guidance**: Provide example query

## 5. Traceability & Recording

### 5.1 Redaction & Privacy
- NEVER include biological or system-specific user prefixes
- Replace sensitive prefixes with `[REDACTED]`
- NEVER log API keys or tokens

### 5.2 Contextual Documentation
- Store session records in `docs/conversations/`
- Save workflow as `docs/implementation-plans/`

## 6. Composition by Higher-Level Skills

- This skill can be called repeatedly with different credential values
- Consider project-specific opencode.json for team-shared configs

***

## Design Appendix

| Feature | Rationale |
|:---|:---|
| JSONC Support | OpenCode config uses JSONC, not strict JSON |
| Env Var Interpolation | Enables secure credential handling |
| Alphabetical Ordering | Consistency with mcp-management |
| Scope Selection | Respects user's isolation preferences |
| Clear Restart Requirement | Config only loads on startup |
| Functional Test Guidance | Ensures working configuration |

## Related Skills
- [`mcp-management`](../mcp-management/SKILL.md)
- [`mcp-cross-tool-config-sync`](../mcp-cross-tool-config-sync/SKILL.md)
- [`opencode-permission-config`](../opencode-permission-config/SKILL.md)
- [`opencode-provider-persistence-config`](../opencode-provider-persistence-config/SKILL.md)
- [`opencode-jsonc-util`](../opencode-jsonc-util/SKILL.md)
- [`is-this-command-safe`](../is-this-command-safe/SKILL.md)
```

#### opencode-remote-mcp-setup/scripts/validate-opencode-mcp.py (200 lines)
```python
#!/usr/bin/env python3
\"\"\"
Validation script for OpenCode MCP configuration.
Checks that the mcp section in opencode.json follows the expected schema.
\"\"\"

import json, subprocess, sys, os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

def load_opencode_config(file_path: str) -> Dict[Any, Any]:
    \"\"\"Load OpenCode config file via opencode-jsonc-util base skill.\"\"\"
    script_dir = Path(__file__).resolve().parent.parent.parent
    reader = script_dir / "opencode-jsonc-util" / "scripts" / "read-jsonc.py"
    if not reader.exists():
        print(f"ERROR: opencode-jsonc-util not found at {reader}", file=sys.stderr)
        sys.exit(1)
    try:
        result = subprocess.run(
            [sys.executable, str(reader), file_path],
            capture_output=True, text=True, check=True, timeout=10
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: opencode-jsonc-util failed: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def validate_mcp_section(config: Dict[Any, Any]) -> List[str]:
    \"\"\"Validate the mcp section.\"\"\"
    errors = []
    if 'mcp' not in config:
        return errors
    mcp_section = config['mcp']
    for server_name, server_config in mcp_section.items():
        if not isinstance(server_config, dict):
            errors.append(f"MCP server '{server_name}' must be an object")
            continue
        if 'type' not in server_config:
            errors.append(f"MCP server '{server_name}' missing 'type'")
            continue
        server_type = server_config['type']
        if server_type == 'local':
            errors.extend(_validate_local_server(server_name, server_config))
        elif server_type == 'remote':
            errors.extend(_validate_remote_server(server_name, server_config))
        else:
            errors.append(f"Invalid type '{server_type}'")
    return errors

def _validate_local_server(server_name: str, config: Dict[Any, Any]) -> List[str]:
    errors = []
    if 'command' not in config:
        errors.append(f"Local server '{server_name}' missing 'command'")
    if 'args' not in config:
        errors.append(f"Local server '{server_name}' missing 'args'")
    return errors

def _validate_remote_server(server_name: str, config: Dict[Any, Any]) -> List[str]:
    errors = []
    if 'url' not in config:
        errors.append(f"Remote server '{server_name}' missing 'url'")
    has_headers = 'headers' in config and isinstance(config['headers'], dict)
    has_oauth = 'oauth' in config and isinstance(config['oauth'], dict)
    if not has_headers and not has_oauth:
        errors.append(f"Remote server '{server_name}' needs 'headers' or 'oauth'")
    if 'enabled' in config and not isinstance(config['enabled'], bool):
        errors.append(f"'enabled' must be boolean")
    return errors

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate-opencode-mcp.py <path-to-opencode.json>")
        sys.exit(1)
    config_path = os.path.expanduser(sys.argv[1])
    config = load_opencode_config(config_path)
    errors = validate_mcp_section(config)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("SUCCESS: OpenCode MCP configuration is valid")

if __name__ == '__main__':
    main()
```

### Deferred Forward References
None — all cross-referenced skills exist in HEAD or committed in C1/C3 of same batch.

---

## C3: feat(mcp): add remote MCP support and OpenCode generators

### Files

**New (untracked):**
- `.agents/skills/mcp-management/scripts/test-pipe.py` — 112 lines

**Modified (tracked):**
- `.agents/skills/mcp-management/SKILL.md` — +82/-13 (8 hunks)
- `.agents/skills/mcp-cross-tool-config-sync/SKILL.md` — +28/-1 (6 hunks)
- `.agents/skills/mcp-cross-tool-config-sync/scripts/generate-configs.py` — +50/-3 (2 hunks)

### Hunks

#### mcp-management/SKILL.md — Hunk 1 (Section 1.2 Remote MCP Discovery)
```diff
@@ -19,7 +19,17 @@
-    - **URL Handling**: For web links, ALWAYS use the `firecrawl` MCP tool to extract detailed technical specifications.
+    - **URL Handling**: For web links, ALWAYS use the `webfetch` tool to extract detailed technical specifications.
+
+### 1.2 Remote MCP Discovery
+- **Transport Identification**: Determine if the MCP server uses stdio (local) or HTTP/WebSocket (remote)
+  - Local: `command` and `args`
+  - Remote: `url` endpoint and auth methods
+- **Authentication Method Identification**:
+  - Bearer Token: `Authorization: Bearer <token>`
+  - OAuth 2.0: `clientId`, `clientSecret`, `tokenUrl`, `scopes`
+  - API Key: Custom headers like `X-API-Key`
+- **URL Extraction**: Extract exact WebSocket/HTTP endpoint URL
```

#### mcp-management/SKILL.md — Hunk 2 (Section 2.3 Remote Server Schema)
```diff
@@ -50,25 +60,59 @@
+### 2.3 Remote Server Schema
+
 "example-server": {
-  "command": "/path/to/binary",
-  "args": ["--option"],
-  "env": { "API_KEY": "SECRET_VALUE" }
+"remote-server-name": {
+  "url": "https://mcp.example.com/mcp",
+  "headers": { "Authorization": "Bearer {env:API_KEY}" },
+  "enabled": true
 }
 ```
+
+**Schema Fields**:
+- `url` (required): WebSocket or HTTP endpoint
+- `headers` (optional): HTTP headers with `{env:VAR_NAME}` interpolation
+- `oauth` (optional): OAuth 2.0 object
+- `enabled` (optional): boolean, default true
+- Remote servers MUST NOT include `command` or `args`
```

#### mcp-management/SKILL.md — Hunks 3-4 (Split stdio/remote workflows)
```diff
 ## 3. Integration Workflow
-1. **Discovery**: Research the server's documentation
+The agent MUST follow different workflows based on server transport type:
+
+### 3.1 Stdio Server Workflow
+1. Discovery → 2. Path Verification → 3. Draft Config → 4. Insertion → 5. Verification (§4.1)
+
+### 3.2 Remote Server Workflow
+1. Discovery → 2. Auth Method Selection → 3. Credential Gathering → 4. Draft Config → 5. Insertion → 6. Verification (§4.2)
```

#### mcp-management/SKILL.md — Hunk 5 (Section 4 verification split)
```diff
+### 4.1 Stdio Server Verification Protocol
+For stdio transport:
 1. JSON Lint: `jq . <config_file>`
 2. Command Dry-Run: `--help` or version flag
 3. Functional Pipe Test: JSON-RPC pipe test
+
+### 4.2 Remote Server Verification Protocol
+For HTTP/WebSocket transport:
+1. JSON Lint: `jq . <config_file>`
+2. Restart Required: Notify user
+3. Functional Test: After restart, verify with meaningful query
```

#### mcp-management/SKILL.md — Hunk 6 (Related Skills)
```diff
+## Related Skills
+
+- [`opencode-remote-mcp-setup`](../opencode-remote-mcp-setup/SKILL.md)
+- [`mcp-cross-tool-config-sync`](../mcp-cross-tool-config-sync/SKILL.md)
```

---

#### mcp-cross-tool-config-sync/SKILL.md — Hunk 1 (Section 4 table)
```diff
@@ -100,6 +100,8 @@
+| OpenCode (Global) | `<user-home>/.config/opencode/opencode.json` | `mcp` | known |
+| OpenCode (Project) | `./opencode.json` | `mcp` | known |
```

#### mcp-cross-tool-config-sync/SKILL.md — Hunk 2 (Section 8 generators)
```diff
@@ -301,6 +303,14 @@
+| `gen_opencode` | `generated/opencode/opencode.json` | rename `mcpServers` → `mcp`; handles `type: remote` |
+
+**Remote-server note**: `gen_opencode` is the only generator handling `type: remote`, `url`, `headers`.
+OpenCode's [remote MCP schema](../opencode-remote-mcp-setup/SKILL.md) supports both stdio and HTTP/WebSocket.
```

#### mcp-cross-tool-config-sync/SKILL.md — Hunk 3 (output example)
```diff
@@ -346,7 +356,11 @@
+#     wrote generated/claude-desktop/claude_desktop_config.json
+#     wrote generated/cursor/mcp.json
+#     wrote generated/windsurf/mcp_config.json
+#     wrote generated/opencode/opencode.json
```

#### mcp-cross-tool-config-sync/SKILL.md — Hunk 4 (deploy map)
```diff
@@ -382,6 +396,8 @@
+| OpenCode (Global) | `<user-home>/.config/opencode/opencode.json` | ... |
+| OpenCode (Project) | `./opencode.json` | ... |
```

#### mcp-cross-tool-config-sync/SKILL.md — Hunk 5 (verification table)
```diff
@@ -439,6 +455,7 @@
+| OpenCode | Restop opencode client; verify MCP servers appear in server list |
```

#### mcp-cross-tool-config-sync/SKILL.md — Hunk 6 (Related Skills section)
```diff
@@ -568,7 +585,14 @@
-## 15. Related Conversations & Traceability
+## 15. Related Skills
+
+- [`mcp-management`](../mcp-management/SKILL.md)
+- [`opencode-remote-mcp-setup`](../opencode-remote-mcp-setup/SKILL.md)
+- [`tool-config-schema-probe`](../tool-config-schema-probe/SKILL.md)
+- [`opencode-jsonc-util`](../opencode-jsonc-util/SKILL.md)
+
+## 16. Related Conversations & Traceability
```

---

#### mcp-cross-tool-config-sync/scripts/generate-configs.py — Hunk 1 (new generators)
```diff
@@ -125,7 +125,39 @@ def gen_jetbrains(...):
+def gen_claude_desktop(canonical):
+def gen_cursor(canonical):
+def gen_windsurf(canonical):
+def gen_opencode(canonical):  # rename mcpServers→mcp, drop inputs
+
+GENERATORS = (..., gen_claude_desktop, gen_cursor, gen_windsurf, gen_opencode)
```

#### mcp-cross-tool-config-sync/scripts/generate-configs.py — Hunk 2 (deploy targets)
```diff
@@ -141,6 +173,22 @@ DEPLOY_TARGETS:
+    "claude-desktop": ("../claude/claude_desktop_config.json", "generated/claude-desktop/..."),
+    "cursor": ("../.cursor/mcp.json", "generated/cursor/mcp.json"),
+    "windsurf": ("../.codeium/windsurf/mcp_config.json", "generated/windsurf/..."),
+    "opencode": ("../.config/opencode/opencode.json", "generated/opencode/..."),
```

#### New: mcp-management/scripts/test-pipe.py (112 lines)
```python
#!/usr/bin/env python3
\"\"\"Test an stdio MCP server — perform MCP initialize handshake then tools/list.
Usage:
    python3 scripts/test-pipe.py --command <command> [--args '["arg1","arg2"]'] [--timeout 15]
\"\"\"

from __future__ import annotations
import argparse, json, subprocess, sys, threading

def read_line(stream, timeout, buffer):
    try:
        line = stream.readline()
        if line: buffer.append(line)
    except ValueError: pass

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", required=True)
    parser.add_argument("--args", default="[]")
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()

    cmd_args = json.loads(args.args)
    proc = subprocess.Popen([args.command, *cmd_args], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def send(msg):
        proc.stdin.write(json.dumps(msg) + "\\n")
        proc.stdin.flush()

    def recv(timeout):
        buffer = []
        thread = threading.Thread(target=read_line, args=(proc.stdout, timeout, buffer))
        thread.daemon = True; thread.start(); thread.join(timeout)
        return json.loads(buffer[0]) if buffer else None

    # Phase 1: Initialize
    send({"jsonrpc":"2.0","id":1,"method":"initialize",
          "params":{"protocolVersion":"2024-11-05","capabilities":{},
                     "clientInfo":{"name":"opencode-test","version":"1.0.0"}}})
    init_resp = recv(args.timeout)
    if not init_resp or "result" not in init_resp:
        print("ERROR: initialize failed", file=sys.stderr); proc.kill(); return 1
    si = init_resp["result"].get("serverInfo",{})
    print(f"  server: {si.get('name','?')} v{si.get('version','?')}")

    # Phase 2: Initialized notification
    send({"jsonrpc":"2.0","method":"notifications/initialized"})

    # Phase 3: tools/list
    send({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})
    tool_resp = recv(args.timeout); proc.kill()
    if not tool_resp or "result" not in tool_resp:
        print("ERROR: tools/list failed", file=sys.stderr); return 1
    tools = tool_resp["result"].get("tools",[])
    print(f"SUCCESS: {len(tools)} tools available")
    for t in tools: print(f"  - {t.get('name','?')}: {t.get('description','')[:80]}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

### Deferred Forward References
None — opencode-jsonc-util and opencode-remote-mcp-setup committed in C1/C2 of same batch; mcp-management, tool-config-schema-probe exist in HEAD.

---

## C4: feat(skill): add opencode-permission-config skill

### Files

**New (untracked):**
- `.agents/skills/opencode-permission-config/AGENTS.md` — 41 lines
- `.agents/skills/opencode-permission-config/SKILL.md` — 621 lines
- `.agents/skills/opencode-permission-config/scripts/verify-permission-pattern.py` — 128 lines
- `.agents/skills/opencode-permission-config/specs/default-config.json` — 1 line
- `.agents/skills/opencode-permission-config/specs/py-compile-allow.json` — 8 lines
- `.agents/skills/opencode-permission-config/specs/full-config.json` — 107 lines

**Modified (tracked):** None — AGENTS.md row already exists in HEAD.

### New File Content Summaries

#### opencode-permission-config/AGENTS.md (41 lines)
Companion bridge with YAML frontmatter. Purpose/When-to-Use (configure permission.bash, debug pattern gotcha, edit opencode.json, understand flat vs object form). Files & Scripts table (verify-permission-pattern.py, 3 specs). Cross-References to command-autoapprove-onboarding, is-this-command-safe, vscode-terminal-autoapprove-audit, mcp-cross-tool-config-sync.

#### opencode-permission-config/SKILL.md (621 lines)

**Section 1 — Permission Config Format**: String form (flat action `"allow"`/`"ask"`/`"deny"`) vs Object form (pattern-based by glob). Lists which tools accept pattern objects (`read`, `edit`, `glob`, `grep`, `list`, `bash`, `task`, `external_directory`, `lsp`, `skill`) vs flat-only (`todowrite`, `question`, `webfetch`, `websearch`, `doom_loop`).

**Section 2 — Pattern Matching Semantics**:
- Glob matching table with examples
- **CRITICAL GOTCHA**: Last-matching-rule wins (opposite of firewall ACL). Common mistake: placing `"*": "ask"` after specific rules. Correct: `"*": "ask"` FIRST, specific rules AFTER.
- Insertion order discipline: catch-all first, specific patterns in increasing specificity.

**Section 3 — Editing Workflow**: Project/global path locations, editing the permission block, restart requirement (no hot-reload).

**Section 4 — Testing & Verification**:
- Manual verification after restart
- Script-based pattern verification (3 modes): inline JSON, direct opencode.json (JSONC-aware), pattern inventory
- Spec-based regression testing (6-test py-compile-allow, 107-test full-config)
- Wrong-order detection via script
- **Real-Command Verification Protocol**: One command at a time, observe permission prompts, never multi-command batches, document outcomes.

**Section 5 — Troubleshooting**: 4-row symptom/cause/fix table (pattern ignored → catch-all ordering; no effect → no restart; broad matches → narrow glob; syntax error → validate with json.tool).

**Section 6 — Pattern Design Decisions** (10 sub-sections):
- 6.1: Always-SAFE commands (echo, which, pwd, true, false, etc.)
- 6.2: SAFE-WITH-QUALIFICATION (cat, python3, markdownlint-cli2)
- 6.3: Read-Only Git subcommands (branch safe-forms, remote safe-forms, stash list/show, -C patterns)
- 6.4: Git -C for any repo path
- 6.5: SAFE-IF-PIPED tradeoffs (ls, cat, grep allowed; find, sort NOT allowed)
- 6.5.1: Broad-Allow + Narrow-Deny/Ask Content Guards (fnmatch limitation workaround)
- 6.6: Explicit Ask Patterns for unsafe git commands (documentation guardrails)
- 6.7: VSCode autoApprove cross-reference (ported patterns table, content-guard ported, excluded)
- 6.8: cd Patterns (chain risk accepted)
- 6.9: awk Content-Guard Worked Example (full problem→solution→verification→generalization)

Plus: Composition Rationale, Related Skills, Source Rules, Composition by Higher-Level Skills.

#### opencode-permission-config/scripts/verify-permission-pattern.py (128 lines)
Loads permission config (JSON string or file path, tries opencode-jsonc-util reader first). `extract_bash_permissions()` handles nested `permission.bash` format. `evaluate()` applies fnmatch last-match-wins. `run_spec()` runs spec file with PASS/FAIL per case. Supports `OPENCODE_PERMISSION_CONFIG` env var. Prints verdict `command → action (matched 'pattern')`.

#### specs/default-config.json (1 line)
```json
{"*": "ask", "python3 -m py_compile *": "allow"}
```

#### specs/py-compile-allow.json (8 lines, 6 tests)
3 py_compile → allow; 3 generic (ls, git status, rm) → ask.

#### specs/full-config.json (107 lines, 107 tests)
Comprehensive: echo/which/pwd (allow), ls variants, git (18 read-only, 5 -C, 15 destructive, 4 --help), python3 (3), mkdir (2), brew (4), npm (3), pg_restore, sed, cut, du, readlink, ffprobe, wc, head, tail, less, lsof, mdls, diff, command -v (allow); rm/mv/npm install/brew install (ask); cd chain risk (3 allow — accepts risk).

### Deferred Forward References
- `fnmatch-content-guard-pattern` (§6.5.1, §6.9, Composition Rationale) — to be added to Related Skills when fnmatch skill is committed in subsequent batch
