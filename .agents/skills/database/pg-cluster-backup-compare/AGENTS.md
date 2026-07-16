# PostgreSQL Cluster Backup & Compare — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to back up a full PostgreSQL cluster (globals + per-DB custom-format dumps) from a remote server over SSH using
the length-prefixed stream protocol, or compare two cluster dumps to surface role drift, schema drift, and data volume
differences across environments.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification steps.
Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [pg-cluster-mirror](../pg-cluster-mirror/SKILL.md) — restores ClusterSplit dumps onto a target cluster with
audit-before-act safety
- [postgres-local-dump-restore](../../postgres-local-dump-restore/SKILL.md) — local single-DB restore counterpart
- [env-example-creation](../../env-example-creation/SKILL.md) — companion for sanitizing fetched `.env` files

## Scripts

- `scripts/Sync-RemoteDatabaseBackup.ps1` — PowerShell orchestrator (local)
- `scripts/parse_dotenv_and_stream_pg_dump.bash` — bash helper (executed remotely via SSH stdin)
