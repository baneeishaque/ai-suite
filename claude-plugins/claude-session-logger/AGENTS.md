# AGENTS.md

## Purpose

`claude-session-logger`: Claude Code hooks logger. Separate fork of
`copilot-plugins/copilot-session-logger` (itself an Option A port of
`opencode-plugins/opencode-logger.ts`), rewritten for the Claude Code
hooks contract. Records every Claude session as multi-doc YAML + JSONL
under `.claude/run-logs/<sessionId>/` so
`opencode-session-*-extractor` skills keep working on Claude sessions.

## Ownership

- Owner: repo maintainer (dk). No separate team.
- Upstream model reference: `opencode-plugins/opencode-logger.ts` (Turn/Step,
  `formatLocal`, `buildYAML` semantics). Sibling references:
  `cline-plugins/cline-session-logger` and
  `copilot-plugins/copilot-session-logger` (hook transport, pending-file
  crash-safety, extractor-compatible schema, nested subagents). This tree
  ports, never modifies, any of them.
- Claude references: `code.claude.com` hooks-guide + hooks reference
  (event schemas, matcher rules, silent-logger contract), and the live
  envelope shapes in `~/.claude/projects/<slug>/<session>.jsonl`.

## Local Contracts

- Runtime is `node` under `mise` only. No `bun`.
- Full-lifecycle dispatch in `lib/router.js` on `hook_event_name`:
  `SessionStart` (source/model/session_title/resume extras),
  `UserPromptSubmit`, `PreToolUse` (`tool_use_id` first-class),
  `PostToolUse` (`tool_response` + `duration_ms`), `PostToolUseFailure`
  (`error`, `is_interrupt`), `PostToolBatch`, `Stop`
  (`last_assistant_message`), `StopFailure`, `SubagentStart/Stop`,
  `Pre/PostCompact`, `TaskCreated/Completed`, `Pre/PostModelSwitch`
  (router handles them; omitted from `settings-snippet.json` because
  older CLIs reject them as unknown events),
  `SessionEnd` (`reason`). No launcher shims: each event's command in
  `settings-snippet.json` invokes `lib/run-hook.js` directly, with
  mise/homebrew bin dirs prepended (GUI-spawned hosts have no node).
- Silent-logger contract: stdout stays EMPTY, exit 0. Claude shows most
  hook stdout only in the debug log, so printing nothing keeps the log
  out of the transcript. Diagnostics go to `~/.claude-hook-errors.log`
  (plus workspace-local `hook-errors.log` when `cwd` is known).
- Install is user-level only (v1): merge `settings-snippet.json` into
  `~/.claude/settings.json` via the `jq` command in its `$comment`
  (single JSON docs cannot symlink). No workspace hook files are shipped.
- Hooks are separate processes: all state round-trips through
  `.claude/run-logs/<sessionId>/state.json` (`liveTurn` + `subTurns` +
  `activeSubagent` + `pendingFile`). No in-memory continuity assumptions.
- Fail-open always: every invocation ends exit 0 with empty stdout.
- `last_assistant_message` is the primary final-text source on
  `Stop`/`SubagentStop` (no transcript race by design); the transcript
  hybrid is enrichment, not backfill.
- Transcript hybrid (`lib/claude-transcript.js`): parses
  `transcript_path` JSONL envelopes (user/assistant text + thinking
  blocks, `tool_use` pairing, `uuid/parentUuid` chains, per-message
  `model`/`usage`, `gitBranch`, `version`; sidechain entries skipped)
  into the header (model, `git_branch`, `claude_version`, usage rollup,
  title) plus canonical `transcript.yaml`. Format drift tolerated; any
  failure swallowed. Raw hook payloads always land in
  `<session>.payloads.jsonl`.
- Tool arg summarizers (`ARG_SUMMARIZERS`) cover the Claude inventory
  (Bash/Edit/Write/Read/Glob/Grep/Task/WebFetch/TodoWrite, `mcp__*`
  flagged); unknown tools fall back to a capped raw dump.
- Subagents nest: `agent_id` on tool events (and the Start bracket)
  routes calls into `state.subTurns[agent_id]`; `SubagentStop` finalizes
  a `{subagent: {id, type}, ...turn}` doc, enriched by the nested hybrid
  over `agent_transcript_path` (usage rollup + transcript link);
  `Stop`/`SessionEnd` flush any still-open bracket first.
- `SessionEnd` is the true close (reason stamped, live turn flushed) —
  Cline/Copilot have no equivalent; rely on it, not on Stop, for
  session completeness.
- Pending files (`NNN-pending-*.yaml`) are crash-safety evidence: only the tracked
  `pendingFile` is ever deleted, never promoted. Orphans from crashed sessions
  are left untouched.
- User-only turns (no assistant steps) produce no turn file (matches opencode v2).
- Output schema adds `session.origin: claude`; session IDs are Claude
  `session_id`s.
- Safety: the agent must not edit hook commands without manual approval
  (it could otherwise rewrite its own logger mid-run).

## Work Guidance

- Keep the runner thin; all logic in `lib/` (`core.js` model, `io.js`
  files, `router.js` dispatch, `claude-transcript.js` hybrid).
- Test payloads via `tests/helpers/claude-fixtures.js` (Claude hook
  shapes + envelope builders); drive via `handle()` from `lib/router.js`
  with `cwd: tmpDir` (hermetic, no chdir).
- When the transcript format drifts, extend `lib/claude-transcript.js`
  parsers — never the hook-event path.

## Verification

- `npm test` (`node --test tests/layer1/*.test.js tests/layer2/*.test.js`): 24 tests,
  CC-HK (mapping incl. failures/batch/tasks/switches), CC-SUB (nested +
  agent transcripts), CC-TR (envelopes, sidechain, usage), CC-STOP/END
  (final text, errors, true close), CC-RC (recovery).
- Stdin drill: pipe each event JSON through `lib/run-hook.js`, assert
  EMPTY stdout, exit 0, and header + `001-*.yaml` + `.jsonl` +
  `.turns.jsonl` artifacts.

## Child DOX Index

- No child docs. Test helpers live under `tests/helpers/` (no separate contract).
