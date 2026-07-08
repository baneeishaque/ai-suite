---
name: microsoft-graph-file-download
description: Generic primitive to download files from Microsoft Graph API using delegated authentication (device code flow or access token).
category: Cloud-API-Integration
---

# Microsoft Graph File Download Skill (v1)

## Composition Rationale

This skill is a **base skill** owning a generic primitive: downloading files from Microsoft Graph API (OneDrive, SharePoint, Teams) using delegated authentication. It is extracted as a separate skill because multiple domain-specific composers (SharePoint backup, OneDrive sync, Teams file export) need this exact primitive. Inlining would split the SSOT and duplicate token handling, Graph API pagination, and error recovery logic.

Known composers:
- `sharepoint-specific-file-backup` — pipes SharePoint file identifiers to this skill
- `sharepoint-delta-polling-backup` — uses delta queries then downloads changed files via this skill
- Future: `onedrive-selective-backup`, `teams-channel-file-export`

## Environment & Dependencies

### Required Tools
- `python3` (3.12+) — primary runtime
- `uv` (optional, for dependency management) or `pip`
- Microsoft Graph Python SDK: `msgraph-sdk`, `azure-identity`

### Installation
```bash
# Using uv (recommended)
uv pip install msgraph-sdk azure-identity

# Or using pip
pip install msgraph-sdk azure-identity
```

### Authentication
Supports two delegated auth modes:
1. **Device Code Flow** (interactive) — for initial auth and manual runs
2. **Access Token** (non-interactive) — for automated runs with cached token

Token caching uses `azure-identity`'s `TokenCachePersistenceOptions` (file-based cache at `~/.msgraph-token-cache.json`).

## Operational Logic

### Public Contract (CLI)

```bash
python3 scripts/download-graph-files.py \
    --drive-id <drive-id> \
    --item-ids <item-id-1> <item-id-2> ... \
    --output-dir <path> \
    [--access-token <token>] \
    [--tenant-id <tenant-id>] \
    [--client-id <client-id>] \
    [--use-device-code] \
    [--metadata-only]
```

**Inputs:**
- `--drive-id` (required): Microsoft Graph drive ID (from SharePoint site drives)
- `--item-ids` (required): One or more item IDs or paths (e.g., `root:/Documents/file.docx`)
- `--output-dir` (required): Local directory to save downloaded files
- `--access-token` (optional): Pre-authenticated access token (for automation)
- `--tenant-id` (optional): Azure AD tenant ID (for device code flow)
- `--client-id` (optional): Azure AD app client ID (for device code flow)
- `--use-device-code` (flag): Force device code flow even if token provided
- `--metadata-only` (flag): Only fetch metadata (ETag, lastModifiedDateTime), skip content download

**Outputs (stdout JSON Lines):**
```json
{"item_id": "01ABC...", "name": "file.docx", "path": "/Documents/file.docx", "size": 12345, "etag": "\"{ETAG},1\"", "last_modified": "2026-06-26T10:30:00Z", "download_url": "https://...", "local_path": "/output/file.docx", "status": "success"}
{"item_id": "01DEF...", "name": "file2.pdf", "status": "error", "error": "Item not found"}
```

### Internal Steps

1. **Authenticate**: Get access token via device code flow or use provided token
2. **Initialize Graph Client**: Create `GraphServiceClient` with token credential
3. **Process Each Item**: For each item ID/path:
   a. Resolve item metadata (GET `/drives/{drive-id}/items/{item-id}` or `root:/{path}`)
   b. If `--metadata-only`: output metadata and continue
   c. Download content (GET `/drives/{drive-id}/items/{item-id}/content` with redirect handling)
   c. Save to output directory preserving folder structure
   d. Output JSON line with metadata + local path
4. **Error Handling**: Continue on individual item failures, report in JSON output

### Token Management

- Device code flow: `DeviceCodeCredential(tenant_id, client_id, cache_persistence_options=...)`
- Token cache: Automatically persisted to `~/.msgraph-token-cache.json`
- Non-interactive: Reuses cached token if not expired; falls back to device code if expired and `--use-device-code` set

## Scripts

- [scripts/download-graph-files.py](scripts/download-graph-files.py) — Main CLI entry point
- [scripts/auth-helper.py](scripts/auth-helper.py) — Token acquisition and caching logic
- [scripts/graph-client.py](scripts/graph-client.py) — GraphServiceClient wrapper with retry logic

## Related Skills

- **Composers**: `sharepoint-specific-file-backup`, `sharepoint-delta-polling-backup`
- **Base**: None (this is a base skill)

## Source Rules

- [AI Rule Standardization Rules](../../../ai-agent-rules/ai-rule-standardization-rules.md)
- [Skill Factory](../../../.agents/skills/skill-factory/SKILL.md)
- [Scripting Language Selection Rules](../../../ai-agent-rules/scripting-language-selection-rules.md) — Tier 1 (Python) selected per §2.3

## Composition by Higher-Level Skills

| Composer | Composition Mechanism |
|---|---|
| `sharepoint-specific-file-backup` | Calls `scripts/download-graph-files.py` with item IDs extracted from SharePoint URLs; consumes JSON Lines output to commit files to GitHub |
| `sharepoint-delta-polling-backup` | Calls `scripts/download-graph-files.py` with item IDs from delta query results; uses `--metadata-only` first to compare ETags, then full download for changed items |

