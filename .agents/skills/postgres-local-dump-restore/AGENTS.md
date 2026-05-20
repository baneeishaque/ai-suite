# AGENTS.md (Postgres Local Dump Restore)

Refer to [SKILL.md](./SKILL.md) for the active operational protocol.

## When to invoke

- The user says any variant of *"my `.env` has a Postgres URL — make it work locally"*, *"load the latest
  production dump"*, *"create that role"*, or *"restore the dump into my dev DB"*.
- A Django / Node / Rails project's local boot fails with `FATAL: role "<x>" does not exist` or
  `FATAL: database "<x>" does not exist` against `localhost:5432`.
- A `db_dumps/` directory is present in the workspace (or an adjacent shared folder) and the user wants its
  newest file loaded into a development cluster.

## Mandates

- **Zero Omission**: All `psql` / `pg_restore` flags MUST be passed through verbatim; never abbreviate
  `--no-owner --no-privileges --clean --if-exists`.
- **Credential Hygiene**: `PGPASSWORD` and `.env` values MUST NOT appear in commit messages, plan files, or
  user-visible summaries beyond a one-line masked URL.
- **Bootstrap Minimalism**: Created roles get `CREATEDB` only — never `SUPERUSER`.
- **Restore-Only**: This skill MUST NOT delete dumps or overwrite the source `.env`.

This skill implements the Industrial standard for local Postgres restore following agentskills.io protocol.
