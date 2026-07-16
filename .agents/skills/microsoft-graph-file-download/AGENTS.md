# Microsoft Graph File Download — Companion Bridge

## Purpose
This file is the bridge for non-skill-aware runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies
- Need to download files from Microsoft Graph API (OneDrive, SharePoint, Teams)
- Using delegated authentication (device code flow or cached token)
- Generic file download primitive — domain-agnostic
- Multiple files/items need to be downloaded with metadata preservation

## Operational Procedure
Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References
- Composer: `sharepoint-specific-file-backup` — pipes SharePoint file identifiers to this skill
- Com`sharepoint-delta-polling-backup` — uses delta queries then downloads changed files via this skill
- Base skill: None (this is a base skill)
