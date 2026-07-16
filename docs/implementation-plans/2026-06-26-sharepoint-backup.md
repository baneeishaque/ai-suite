# [SharePoint Online Document Backup to GitHub] (v2)

## Rule Compliance Reference
- [Agent Planning Rules](../ai-agent-rules/ai-agent-planning-rules.md)
- [Shell Execution Rules](../ai-agent-rules/shell-execution-rules.md)
- [AI Rule Standardization Rules](../ai-agent-rules/ai-rule-standardization-rules.md)
- [Skill Factory](../.agents/skills/skill-factory/SKILL.md)
- [GitHub Workflow Creation](../.agents/skills/github-workflow-creation/SKILL.md)
- [GitHub Repo Create](../.agents/skills/gh-repo-create/SKILL.md)

## Starting Point
User wants to backup specific SharePoint Online documents to a GitHub repository:
- Environment: SharePoint Online (Microsoft 365)
- Authentication: User delegation (interactive) - device code flow
- Storage: GitHub repository (private)
- Scope: Specific files (user will provide URLs)
- Trigger: Periodic + webhook-based on changes
- Constraint: No admin access (cannot register Azure AD app)

## Proposed Plan

### Phase 1: Discovery & Setup
1. Create GitHub repository for backups (private) - using `gh-repo-create` skill
2. Identify specific SharePoint files/libraries from user-provided URLs
3. Extract site ID, drive ID, item IDs from SharePoint URLs
4. Document required Microsoft Graph permissions (delegated)

### Phase 2: Core Backup Script (New Skills)
5. **Create base skill**: `microsoft-graph-file-download` - generic primitive to download files from Microsoft Graph API using delegated auth (device code flow)
6. **Create composer skill**: `sharepoint-specific-file-backup` - discovers file metadata from URLs, pipes to base skill, commits to GitHub
7. Test script manually with sample files

### Phase 3: Automation - Periodic Backup (No Admin Required)
8. Create GitHub Actions workflow for scheduled runs using `github-workflow-creation` skill
9. Workflow uses stored GitHub PAT + Microsoft Graph device code flow (interactive auth cached via token cache)
10. Test scheduled workflow execution - **feasible without admin** since it uses user delegation

### Phase 4: Automation - Webhook/Change-based Backup (Admin Required)
11. **Webhook registration requires admin** - Registering SharePoint webhook subscriptions via Microsoft Graph needs `Sites.ReadWrite.All` or `Sites.Manage.All` (admin consent)
12. Alternative: Use GitHub Actions `workflow_dispatch` with manual trigger or scheduled polling for changes
13. **Recommended**: Polling-based approach using Microsoft Graph delta queries (`/drive/items/{id}/delta`) - no admin needed
14. Implement deduplication using ETags/lastModifiedDateTime

### Phase 5: Monitoring & Maintenance
15. Add logging and notification (GitHub Actions summary, optional email/Teams webhook)
16. Document recovery procedures
17. Set up retention policy for GitHub backup history

## Skills to Create (Layered Approach)

### Base Skill: `microsoft-graph-file-download`
- Generic primitive: Download file(s) from Microsoft Graph using delegated auth
- Input: access token, drive ID, item ID(s) or paths
- Output: file content + metadata (ETag, lastModifiedDateTime, @microsoft.graph.downloadUrl)
- Domain-agnostic, reusable for OneDrive, SharePoint, Teams files

### Composer Skill: `sharepoint-specific-file-backup`
- Domain-specific: Parse SharePoint URLs → extract site/drive/item IDs
- Pipe file identifiers to base skill
- Commit downloaded files to GitHub repo with proper commit messages
- Handle token caching for non-interactive runs

### Composer Skill: `sharepoint-delta-polling-backup`
- Domain-specific: Use Microsoft Graph delta queries to detect changes
- Poll periodically via GitHub Actions schedule
- Trigger backup only for changed files
- No admin access required

## Files to Create/Modify
- `/Users/dk/lab-data/ai-suite/docs/implementation-plans/2026-06-26-sharepoint-backup.md` (this plan)
- GitHub repository (to be created via `gh-repo-create`)
- `.agents/skills/microsoft-graph-file-download/SKILL.md` + scripts
- `.agents/skills/sharepoint-specific-file-backup/SKILL.md` + scripts
- `.agents/skills/sharepoint-delta-polling-backup/SKILL.md` + scripts
- `.github/workflows/sharepoint-backup-scheduled.yml`
- `.github/workflows/sharepoint-backup-polling.yml`

## Change History
| Timestamp | Summary of Changes | Rationale |
| :--- | :--- | :--- |
| [2026-06-26 14:30] | Initial plan v1 created | Based on user requirements clarification |
| [2026-06-26 15:45] | Plan v2: Added skill layering, clarified admin constraints | User feedback: no admin access, need URL parsing, webhook requires admin |

## User Questions & Answers
- **Environment**: SharePoint Online (Microsoft 365)
- **Auth Method**: User delegation (interactive) - device code flow
- **Storage**: GitHub repository (private)
- **Scope**: Specific files (user will provide URLs)
- **Triggers**: Both periodic (scheduled) and change-based
- **Admin Access**: NO - cannot register Azure AD app or webhooks
- **URL Parsing**: Need skill to extract site/drive/item IDs from SharePoint URLs
- **Phase 3 (Scheduled)**: Feasible without admin - uses delegated auth + GitHub Actions
- **Phase 4 (Webhook)**: NOT feasible without admin - requires admin consent for webhook registration
- **Alternative to Webhook**: Microsoft Graph delta queries (polling) - no admin needed

## Technical Details

### SharePoint URL Patterns
- Site: `https://{tenant}.sharepoint.com/sites/{site-name}`
- Document Library: `https://{tenant}.sharepoint.com/sites/{site-name}/{library-name}`
- File: `https://{tenant}.sharepoint.com/sites/{site-name}/{library-name}/{path}/{file.ext}`
- File (with ID): `https://{tenant}.sharepoint.com/:x:/s/{site-name}/{sharing-token}`

### Microsoft Graph API Endpoints
- Get site by URL: `GET /sites/{hostname}:/sites/{site-path}`
- Get drives: `GET /sites/{site-id}/drives`
- Get file by path: `GET /drives/{drive-id}/root:/{path}`
- Download file: `GET /drives/{drive-id}/items/{item-id}/content`
- Delta query: `GET /drives/{drive-id}/root/delta`

### Required Delegated Permissions (No Admin Consent)
- `Files.Read` - Read user's files
- `Files.Read.All` - Read all files user has access to
- `Sites.Read.All` - Read all sites user has access to
- `User.Read` - Basic profile
