# PostgreSQL Cluster Mirror — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You need to restore a ClusterSplit PostgreSQL dump (globals.sql + per-DB .dump files) onto a target cluster — either via
a local DSN or through an SSH port-forward tunnel. The mirror is gated by permission preflight, an audit-before-act
report, a mandatory pre-mirror backup, and three DB naming modes.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the five-phase pipeline, naming modes, and all
safety interlocks. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [pg-cluster-backup-compare](../pg-cluster-backup-compare/SKILL.md) — produces ClusterSplit dumps consumed by this
skill
- [staging-env-fetch](../staging-env-fetch/SKILL.md) — companion for fetching `.env` from staging environments
- [postgres-local-dump-restore](../../postgres-local-dump-restore/SKILL.md) — local single-DB restore counterpart

## Scripts

- `scripts/Mirror-DatabaseCluster.ps1` — five-phase mirror orchestrator
- `scripts/Restore-LocalDatabase.ps1` — single-DB local restore
- `scripts/Sync-RemoteDatabaseBackup.ps1` — shared with pg-cluster-backup-compare; used for SSH pre-mirror backup
