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
- Sparse mode: hook payloads carry no assistant text (real payloads
  arrive with tool names undefined), so `thinking`/`response` in
  hook-driven turns stay empty. The canonical `transcript.yaml`
  (see below) carries the full content instead.
- Cline session bridge (`lib/cline-session.js`): every hook also
  resolves Cline's own session (`~/.cline/data/sessions`, override
  via `CLINE_SESSIONS_ROOT` for tests) by workspace + conversation
  timestamp, caches the link in `state.json`, enriches the header
  (real model/title/usage/git branch/`cline_session_id`), and
  rewrites the canonical `transcript.yaml` (thinking + text +
  tool_use/tool_result segmented into turns; `user_input` tags
  stripped; per-step token counts when present). Raw hook payloads
  are always captured to `<task>.payloads.jsonl` (payload shapes
  drift from the docs — this log grounds future mapping).
- Hook payload harvest (verified against live payloads): every hook
  carries `clineVersion` (header provenance — `model` arrives as
  unknown/unknown; the real model comes from session metadata).
  `TaskComplete.taskMetadata.result` is injected as the turn's final
  response (deduped), so even tool-less tasks produce `001-*.yaml`;
  it also lands on the `task.complete` jsonl entry. Every string
  ID-like field in `taskMetadata` (`taskId`, `ulid`, any `*Id`
  spillover) is harvested forward-only into the header
  (`session.ulid`, `session.task_ids`) and the `task.start` /
  `task.complete` jsonl entries (late arrivals on `TaskComplete`
  backfill gaps); top-level `userId` lands in the header
  (`session.user_id`) and jsonl. `user_input`
  wrappers are stripped from human YAML text (titles, turn text);
  machine jsonl and `*.payloads.jsonl` keep raw bytes.
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

- `npm test` (`node --test tests/layer1/*.test.js tests/layer2/*.test.js`): 28 tests,
  layers mirror `opencode-plugins` LG-HK (CL-HK) + LG-RC (CL-RC) conventions,
  plus CL-HK-070 (real shim under GUI-like minimal PATH), CL-HK-071
  (invocation via symlink, the global-install path), CL-SE (session
  bridge: discovery, segmentation, enrichment, transcript rewrite),
  CL-CP (completion harvest: result injection, tag stripping,
  version provenance), and CL-TID (taskMetadata identity: ulid,
  *Id spillover, userId).
- Manual drill: pipe hook JSON through each executable, assert `{"cancel":false}`
  and header + `001-*.yaml` + `.jsonl` + `.turns.jsonl` artifacts.

## Child DOX Index

- No child docs. Test helpers live under `tests/helpers/` (no separate contract).
