# AGENTS.md

## Purpose

`copilot-session-logger`: GitHub Copilot VS Code agent-hooks logger.
Separate fork of `cline-plugins/cline-session-logger` (itself an Option A
port of `opencode-plugins/opencode-logger.ts`), rewritten for the Copilot
hooks contract. Records every Copilot agent session as multi-doc YAML +
JSONL under `.copilot/run-logs/<sessionId>/` so
`opencode-session-*-extractor` skills keep working on Copilot sessions.

## Ownership

- Owner: repo maintainer (dk). No separate team.
- Upstream model reference: `opencode-plugins/opencode-logger.ts` (Turn/Step,
  `formatLocal`, `buildYAML` semantics). Sibling reference:
  `cline-plugins/cline-session-logger` (hook transport, pending-file
  crash-safety, extractor-compatible schema). This tree ports, never
  modifies, either.
- Copilot references: `microsoft/vscode` `extensions/copilot`
  (`src/extension/tools/node` tool inventory, `executionSubagentTool`,
  `trajectory/`), VS Code agent-hooks + hooks-reference docs, and the
  field inventory of `ai-session-exports/github-copilot-chats/`
  `graphify-backends.json` (125 requests: `toolInvocationSerialized`
  parts, `modelId`, `result{details,metadata,timings,errorDetails}`,
  token/credit counters, `variableData`).

## Local Contracts

- Runtime is `node` under `mise` only. No `bun`, no `@vscode/*` imports.
- 8 hook events (`SessionStart`, `UserPromptSubmit`, `PreToolUse`,
  `PostToolUse`, `PreCompact`, `SubagentStart`, `SubagentStop`, `Stop`)
  dispatch in `lib/router.js` on `hook_event_name`. No launcher shims:
  Copilot runs `command` strings, so `hooks-config/`
  `copilot-hooks.example.json` points each event at
  `lib/run-hook.js` (which calls `run()`); commands prepend
  mise/homebrew bin dirs because GUI-spawned VS Code has no node on PATH.
- Stdout is always pure `{"continue":true}` (Copilot contract — exit 0
  parses stdout, 2 blocks, other warns). Never emit Cline's
  `{"cancel":false}` here. Diagnostics go to
  `~/.copilot-hook-errors.log` (plus workspace-local `hook-errors.log`
  when `cwd` is known); stdout stays pure JSON.
- Install is user-level only (v1): copy the example JSON into
  `~/.copilot/hooks/`. No workspace hook files are shipped, so team
  checkouts never double-log.
- Hooks are separate processes: all state round-trips through
  `.copilot/run-logs/<sessionId>/state.json` (`liveTurn` + `subTurns` +
  `activeSubagent` + `pendingFile`). No in-memory continuity assumptions.
- Fail-open always: every invocation prints `{"continue":true}`, never
  blocks Copilot. `stop_hook_active` is logged, never acted on (blocking
  Stop would burn credits in a loop).
- Sparse mode: Copilot hook payloads carry no assistant text or model
  (requested `modelId` is `copilot/auto`), so hook-driven turns record
  tool calls; the canonical `transcript.yaml` carries full content.
- Transcript hybrid (`lib/copilot-transcript.js`): every hook also reads
  `transcript_path` when present and best-effort folds it into the header
  (actual model from `result.details`, never `copilot/auto`; usage rollup
  `promptTokens`/`completionTokens`/`copilotCredits`; `agent`/`mode`;
  title) plus per-request docs (full response markdown, per-request usage
  and timings, `variableData` URIs + ≤500-char snippets, `code_blocks`
  counts, `errorDetails` codes). Format drift is tolerated; any failure
  is swallowed. Raw hook payloads are always captured to
  `<session>.payloads.jsonl` (payload shapes drift from the docs — this
  log grounds future mapping).
- Tool arg summarizers (`ARG_SUMMARIZERS` in `lib/router.js`) cover the
  observed inventory (`run_in_terminal`, `copilot_readFile`,
  `copilot_applyPatch`, `copilot_getErrors`, `copilot_findTextInFiles`,
  `copilot_findFiles`, `copilot_listDirectory`, `copilot_createFile`,
  `copilot_multiReplaceString`, terminal helpers); unknown tools fall back
  to a capped raw dump. Reads are camelCase-tolerant (VS Code tools use
  camelCase, Claude Code snake_case).
- Subagents nest: tool calls inside a `SubagentStart..Stop` bracket route
  to that subagent's live turn (`state.subTurns[agent_id]`); `SubagentStop`
  finalizes a `{subagent: {id, type}, ...turn}` doc into the parent
  sequence; `Stop` flushes any still-open bracket first.
- Pending files (`NNN-pending-*.yaml`) are crash-safety evidence: only the tracked
  `pendingFile` is ever deleted, never promoted. Orphans from crashed sessions
  are left untouched.
- User-only turns (no assistant steps) produce no turn file (matches opencode v2).
- Output schema adds `session.origin: copilot`; session IDs are Copilot
  `session_id`s, not `ses_*`.
- Safety: the agent must not edit hook commands without manual approval
  (it could otherwise rewrite its own logger mid-run).

## Work Guidance

- Keep the runner thin; all logic in `lib/` (`core.js` model, `io.js`
  files, `router.js` dispatch, `copilot-transcript.js` hybrid).
- Test payloads via `tests/helpers/copilot-fixtures.js` (Copilot hook
  shapes + transcript-shaped requests); drive via `handle()` from
  `lib/router.js` with `cwd: tmpDir` (hermetic, no chdir).
- When the transcript format drifts, extend `lib/copilot-transcript.js`
  parsers — never the hook-event path.

## Verification

- `npm test` (`node --test tests/layer1/*.test.js tests/layer2/*.test.js`): 18 tests,
  CP-HK (event mapping), CP-SUB (nested subagents), CP-TR (transcript
  hybrid), CP-STOP (finalize), CP-RC (recovery).
- Stdout drill: pipe each event JSON through `lib/run-hook.js`, assert
  `{"continue":true}` and header + `001-*.yaml` + `.jsonl` +
  `.turns.jsonl` artifacts.

## Child DOX Index

- No child docs. Test helpers live under `tests/helpers/` (no separate contract).
