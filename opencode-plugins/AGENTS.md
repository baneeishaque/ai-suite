# AGENTS.md — opencode-plugins

## Purpose

Owns the opencode plugins developed in this repository, their tests, schemas,
and documentation:

- `opencode-logger.ts` — per-session YAML/JSONL logger plugin.
- `session-yaml-schema.json` — schema for the logger's session YAML.
- `tests/` — bun:test suites for both plugins (unit, hook, opt-in E2E).
- `docs/testing/` — the suite SSOTs (one per plugin).

## Ownership

- Plugin sources, config schemas/examples, `package.json` dependencies and
  runner scripts, test suites, and the `docs/testing/*-suite-overview.md`
  SSOTs all belong to this folder.

## Local Contracts

- **Config resolution is symlink-safe.** Plugins resolve their config from an
  env override or an XDG path — never from `import.meta.url` — because the
  live install loads them through symlinks.
- **E2E is opt-in** (`E2E_RUN=1`), spawns the real `opencode` binary, and must
  set `PWD` in the child env to the scenario directory (a stale `PWD` makes
  opencode attach the session to the wrong project).
- **Live installs are symlinks.** `~/.config/opencode/plugins/<plugin>` points
  into this folder; real (machine-local) config files stay real files next to
  the symlinks.

## Work Guidance

- Use the mise-managed bun: `mise x bun -- bun test --parallel=1 …` from
  `opencode-plugins/`.
- Update the SSOT doc in the same change as any behavior, config-schema, or
  test-ID change.

## Verification

- opencode-logger: `bun run test:hook` + `bun run test:recovery`, then
  `bun run test:e2e`; baseline in `docs/testing/test-suite-overview.md`.
- A live smoke run (`opencode run -f <png> -m <provider/model>`) plus a log
  check for the new-format cap line validates the symlinked install.

## Child DOX Index

- No child AGENTS.md files; this document covers the whole subtree.
