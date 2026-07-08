# Conversation Log — Postgres Local Dump Restore (genesis run)

## Context

Acers backend (Django, cookiecutter-django layout). The user attached `<repo-root>/acers/.env` and asked
whether the `DATABASE_URL` was valid on their machine.

## Sequence

1. **Discovery**: `grep -iE 'postgres|database_url|db_url' <repo-root>/acers/.env` extracted
   `DATABASE_URL=postgresql://myprojectuser:***@localhost:5432/acers_20_01_2026`.
2. **Validation**: `PGPASSWORD=*** psql -h localhost -p 5432 -U myprojectuser -d acers_20_01_2026 -c "SELECT version();"`
   returned `FATAL: role "myprojectuser" does not exist`.
3. **Superuser fallback discovery**: `psql -h localhost -p 5432 -U postgres -d postgres` failed with
   `role "postgres" does not exist`; falling back to OS-user ident auth via
   `psql -h localhost -p 5432 -d postgres -c "SELECT current_user;"` returned the OS user — bootstrap login
   confirmed.
4. **Role + DB bootstrap**:

   ```sql
   CREATE ROLE myprojectuser WITH LOGIN PASSWORD '***' CREATEDB;
   CREATE DATABASE acers_20_01_2026 OWNER myprojectuser;
   ```

5. **Re-validation**: same `psql -U myprojectuser` probe returned `myprojectuser | acers_20_01_2026`.
6. **Dump discovery**: User pointed to `<repo-parent>/db_dumps/`. `ls -lah` listed several files / cluster-dump
   directories. Newest by mtime was
   `acers-production-cluster-12-05-2026-19-19-UTC/acers.dump` (May 12, 2026, 7.9 MB, custom format per
   `file` output).
7. **Restore**:

   ```bash
   PGPASSWORD=*** pg_restore -h localhost -p 5432 -U myprojectuser -d acers_20_01_2026 \
     --no-owner --no-privileges --clean --if-exists -j 4 \
     <repo-parent>/db_dumps/acers-production-cluster-12-05-2026-19-19-UTC/acers.dump
   ```

   Exited 0 with no errors (the production dump's owner `acersuser` was silenced by `--no-owner`; warnings
   from `--clean --if-exists` against an empty target were tolerated per protocol §2.6.1).

8. **Verification**:

   ```sql
   SELECT count(*) AS tables FROM information_schema.tables WHERE table_schema='public';
   -- 80
   ```

## Lessons Encoded into the Skill

- **Cookiecutter-django dual layout**: the `.env` may live at `<repo-root>/.env` or
  `<repo-root>/<django-project>/.env` — the skill checks both (§2.1).
- **Docker hostnames in `.env`**: `POSTGRES_HOST=postgres` is unreachable from the host; the skill
  overrides to `localhost` for local restores (§2.1).
- **Cluster-dump directories**: production dumps may ship as a directory containing `acers.dump`,
  `globals.sql`, and `postgres.dump` — the skill picks the per-DB `.dump` and ignores `globals.sql` for a
  scoped restore (§2.4 / §2.5).
- **OS-user ident as bootstrap superuser**: macOS Homebrew Postgres ships without a `postgres` role; the
  skill probes the OS user first before falling back to `-U postgres` (§2.3.1).
