# Staging Env Fetch — Companion Bridge

## Purpose

This file is the bridge for non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

The local dev server fails to start with a missing environment variable error (e.g. `ImproperlyConfigured`), the local
`.env` file is missing, a developer needs a baseline local environment file from the staging server, or you are
onboarding a new developer who does not yet have a `.env`.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure. The skill uses the `ssh-staging-exec` MCP tool (from the
[`ssh-mcp`](https://www.npmjs.com/package/ssh-mcp) npm package) to fetch `.env` from the staging server remote path,
then writes it to the correct local path. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`SKILL.md`](SKILL.md) — the SSOT
- [env-example-creation](../../env-example-creation/SKILL.md) — companion for sanitizing fetched `.env` into a
`.env.example`
- [pg-cluster-backup-compare](../pg-cluster-backup-compare/SKILL.md) — companion for PostgreSQL backup workflows
- [pg-cluster-mirror](../pg-cluster-mirror/SKILL.md) — companion for PostgreSQL restore workflows

## Scripts

This skill has no local scripts — all operations are performed via the `ssh-staging-exec` MCP tool against the remote
staging server.
