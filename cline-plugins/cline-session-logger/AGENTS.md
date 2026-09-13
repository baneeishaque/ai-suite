# AGENTS.md

## Purpose

`cline-session-logger`: Cline VS Code hooks logger (Option A port of
`opencode-plugins/opencode-logger.ts`). Lives in the `cline-plugins/` container
(future plugins sit beside it as siblings). Records every Cline task as
multi-doc YAML + JSONL under `.cline/run-logs/<taskId>/` so
`opencode-session-*-extractor` skills keep working on Cline sessions.

## Ownership

- Owner: repo maintainer (dk). No separate team.
- Upstream model reference: `opencode-plugins/opencode-logger.ts` (Turn/Step,
  `formatLocal`, `buildYAML` semantics). This tree ports, never modifies, upstream.

## Local Contracts

- Runtime is `node` under `mise` only. No `bun`, no `@cline/*` imports.
- 8 hook executables (`hooks/TaskStart`, `TaskResume`, `UserPromptSubmit`,
  `PreToolUse`, `PostToolUse`, `TaskComplete`, `TaskCancel`, `PreCompact`) are
  extensionless, `chmod +x`, `#!/usr/bin/env bash` PATH-hardened launchers:
  GUI-spawned processes (VS Code from Dock/Finder) have no node on PATH, so
  each shim prepends mise/homebrew bin dirs, resolves its canonical dir via
  `cd -P` (symlink-safe) into `PLUGIN_DIR`, then `exec node $PLUGIN_DIR/lib/run-hook.js` (which calls `run()`
  in `lib/router.js`). Diagnostics go to `~/.cline-hook-errors.log` (plus
  workspace-local `hook-errors.log` when known); stdout stays pure
  `{"cancel":false}`.
- Install is 8 absolute symlinks in `~/Documents/Cline/Hooks/` pointing at
  `hooks/`. No workspace hook dir (Cline runs global+workspace hooks
  concurrently — a workspace copy would double-log every event).
- Hooks are separate processes: all state round-trips through
  `.cline/run-logs/<taskId>/state.json` (`liveTurn` + `pendingFile`). No in-memory
  continuity assumptions.
- Fail-open always: every invocation prints `{"cancel":false}`, never blocks Cline.
- Sparse mode: `thinking`/`response` stay empty (Cline hooks carry no assistant
  text streams). Tool calls are the primary content.
- Pending files (`NNN-pending-*.yaml`) are crash-safety evidence: only the tracked
  `pendingFile` is ever deleted, never promoted. Orphans from crashed sessions
  are left untouched.
- User-only turns (no assistant steps) produce no turn file (matches opencode v2).
- Output schema adds `session.origin: cline`; task IDs are Cline `taskId`s, not `ses_*`.

## Work Guidance

- Keep shims thin; all logic in `lib/` (`core.js` model, `io.js` files, `router.js` dispatch).
- Test payloads via `tests/helpers/cline-fixtures.js`; drive via `handle()` from
  `lib/router.js` with `workspaceRoots: [tmpDir]` (hermetic, no chdir).
- Enable in VS Code via Cline Settings → Features → Enable Hooks.

## Verification

- `npm test` (`node --test tests/layer1/*.test.js tests/layer2/*.test.js`): 13 tests,
  layers mirror `opencode-plugins` LG-HK (CL-HK) + LG-RC (CL-RC) conventions,
  plus CL-HK-070 (real shim under GUI-like minimal PATH) and CL-HK-071
  (invocation via symlink, the global-install path).
- Manual drill: pipe hook JSON through each executable, assert `{"cancel":false}`
  and header + `001-*.yaml` + `.jsonl` + `.turns.jsonl` artifacts.

## Child DOX Index

- No child docs. Test helpers live under `tests/helpers/` (no separate contract).
