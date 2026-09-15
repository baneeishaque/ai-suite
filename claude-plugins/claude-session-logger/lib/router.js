// Claude hooks router: reads one JSON payload from stdin, dispatches by
// hook_event_name, appends to .claude/run-logs/<sessionId>/. Prints
// NOTHING (Claude's silent-logger contract: exit 0, empty stdout keeps the
// session log out of the transcript and the debug log).
import { loadPersisted, resolveBase, savePersisted, loadTurnsFromDisk, sanitizeTaskId, serializeSubTurns, serializeTurn, taskDir, writeJSONL, writeTurnsJSONL, writeYAML } from "./io.js";
import { Turn, finalizeTurn, modelFromTranscript, newSessionState, normalizeResult, reviveTurn, ts } from "./core.js";
import { parseTranscriptFile, writeTranscriptYaml } from "./claude-transcript.js";
import { appendFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

function readStdin() {
  return new Promise((resolve) => {
    let data = "";
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (c) => { data += c; });
    process.stdin.on("end", () => resolve(data));
    // Bound the wait in case stdin stays open.
    setTimeout(() => resolve(data), 5000);
  });
}

function hookTs(payload) {
  const raw = payload?.timestamp;
  if (typeof raw === "string" && raw !== "") {
    const ms = Date.parse(raw);
    if (Number.isFinite(ms)) return new Date(ms).toISOString();
  }
  const n = Number(raw);
  if (Number.isFinite(n) && n > 0) return new Date(n).toISOString();
  return ts();
}

function hydrate(sessionId, dir, payload) {
  // Rebuild state from disk on every invocation (hooks are separate
  // processes; no in-memory state survives).
  const persisted = loadPersisted(dir) ?? {};
  const { turns, header } = loadTurnsFromDisk(dir);
  const state = newSessionState();
  state.turns = turns;
  state.writtenTurns = turns.length;
  state.created = persisted.created ?? header?.session?.created ?? hookTs(payload);
  state.updated = persisted.updated ?? null;
  state.model = persisted.model ?? header?.model ?? null;
  state.title = persisted.title ?? header?.title ?? null;
  state.agent = persisted.agent ?? header?.session?.agent ?? null;
  state.mode = persisted.mode ?? header?.session?.mode ?? null;
  state.cwd = persisted.cwd ?? header?.session?.cwd ?? null;
  state.gitBranch = persisted.gitBranch ?? header?.session?.git_branch ?? null;
  state.claudeVersion = persisted.claudeVersion ?? header?.claude_version ?? null;
  state.resume = persisted.resume ?? header?.session?.resume ?? null;
  state.endReason = persisted.endReason ?? header?.session?.end_reason ?? null;
  state.compactedAt = persisted.compactedAt ?? null;
  state.pendingFile = persisted.pendingFile ?? null;
  state.transcriptTurns = persisted.transcriptTurns ?? null;
  state.usage = persisted.usage ?? header?.usage ?? null;
  state.activeSubagent = persisted.activeSubagent ?? null;
  state.turn = reviveTurn(persisted.liveTurn ?? null);
  state.subTurns = {};
  for (const [id, plain] of Object.entries(persisted.subTurns ?? {})) {
    const t = reviveTurn(plain);
    if (t) state.subTurns[id] = t;
  }
  return { state, persisted };
}

function persist(dir, sessionId, state) {
  savePersisted(dir, {
    created: state.created,
    updated: state.updated,
    model: state.model,
    title: state.title,
    agent: state.agent,
    mode: state.mode,
    cwd: state.cwd,
    gitBranch: state.gitBranch,
    claudeVersion: state.claudeVersion,
    resume: state.resume,
    endReason: state.endReason,
    compactedAt: state.compactedAt,
    writtenTurns: state.writtenTurns,
    pendingFile: state.pendingFile,
    transcriptTurns: state.transcriptTurns,
    usage: state.usage,
    activeSubagent: state.activeSubagent,
    liveTurn: serializeTurn(state.turn),
    subTurns: serializeSubTurns(state.subTurns),
  });
  void sessionId;
}

// The live turn tool calls belong to: the bracketed subagent turn when a
// SubagentStart..Stop bracket is open (tool events carry agent_id too),
// else the main turn.
function ensureTurn(state, userText, userTime) {
  if (state.activeSubagent && state.subTurns[state.activeSubagent]) {
    return state.subTurns[state.activeSubagent];
  }
  if (!state.turn) {
    state.turn = new Turn();
    state.turn.userText = userText ?? "";
    state.turn.userTime = userTime ?? null;
    state.turn.startTime = ts();
  } else if (userText != null && state.turn.userText === "") {
    state.turn.userText = userText;
    state.turn.userTime = userTime ?? state.turn.userTime;
  }
  return state.turn;
}

function completeTurnIfAny(dir, sessionId, state, type) {
  if (finalizeTurn(state)) {
    const idx = state.turns.length - 1;
    writeJSONL(dir, sessionId, { timestamp: ts(), sessionId, type, turnIndex: idx });
    writeTurnsJSONL(dir, sessionId, state.turns[idx], idx);
  }
  state.updated = ts();
  writeYAML(dir, sessionId, state);
  persist(dir, sessionId, state);
}

// Finalize an open subagent turn into a nested turn doc.
function completeSubTurnIfAny(dir, sessionId, state, agentId) {
  const t = agentId ? state.subTurns[agentId] : null;
  if (!t) return false;
  if (t.currentStep) t.currentStep.endTime = ts();
  t.endTime = ts();
  if (t.steps.length === 0 && !t.usage && !t.result) {
    delete state.subTurns[agentId];
    return false;
  }
  const doc = { subagent: { ...(t.agent ?? { id: agentId }) }, ...t.toFields() };
  delete doc.agent; // agent identity lives under subagent
  state.turns.push(doc);
  delete state.subTurns[agentId];
  const idx = state.turns.length - 1;
  writeJSONL(dir, sessionId, { timestamp: ts(), sessionId, type: "subagent.turn", turnIndex: idx, agentId });
  writeTurnsJSONL(dir, sessionId, doc, idx);
  return true;
}

// Attach stop-time assistant text to a live turn, unless already present
// (Stop can refire; never duplicate the response).
function attachAssistantText(turn, model, text) {
  if (!turn || typeof text !== "string" || text === "") return false;
  const seen = turn.steps.flatMap((s) => s.responseText ?? []).join("\n");
  if (seen.includes(text)) return false;
  turn.ensureStep(model).responseText.push(text);
  return true;
}

// Per-tool argument summarizers for the Claude inventory.
// Unknown tools fall back to a capped raw dump. Keeps YAML skimable.
const ARG_SUMMARIZERS = {
  Bash: (i) => ({ command: typeof i?.command === "string" ? i.command.slice(0, 2000) : null }),
  Edit: (i) => ({ file_path: i?.file_path ?? null }),
  Write: (i) => ({ file_path: i?.file_path ?? null }),
  Read: (i) => ({ file_path: i?.file_path ?? null }),
  Glob: (i) => ({ pattern: i?.pattern ?? null }),
  Grep: (i) => ({ pattern: i?.pattern ?? null }),
  Task: (i) => ({ description: i?.description ?? null, subagent_type: i?.subagent_type ?? null }),
  WebFetch: (i) => ({ url: i?.url ?? null }),
  TodoWrite: (i) => ({ todos: Array.isArray(i?.todos) ? i.todos.length : null }),
};

function summarizeArgs(toolName, input) {
  try {
    if (!input || typeof input !== "object") return {};
    const fn = ARG_SUMMARIZERS[toolName];
    if (fn) {
      const out = fn(input) ?? {};
      return Object.fromEntries(Object.entries(out).filter(([, v]) => v != null));
    }
    if (typeof toolName === "string" && toolName.startsWith("mcp__")) {
      return { mcp_tool: toolName };
    }
    const raw = JSON.stringify(input);
    return { _raw: raw.length > 2000 ? raw.slice(0, 2000) : raw };
  } catch { return {}; }
}

export async function handle(payload) {
  const sessionId = sanitizeTaskId(payload?.session_id ?? "unknown");
  const base = resolveBase([payload?.cwd]);
  const dir = taskDir(base, sessionId);
  // Raw payload capture: hook schemas drift across versions; this log
  // grounds future mapping.
  try {
    appendFileSync(
      join(dir, `${sanitizeTaskId(sessionId)}.payloads.jsonl`),
      JSON.stringify({ timestamp: ts(), hook_event_name: payload?.hook_event_name ?? null, payload }) + "\n",
    );
  } catch { /* ignore */ }
  const now = hookTs(payload);
  const event = payload?.hook_event_name;

  switch (event) {
    case "SessionStart": {
      const { state } = hydrate(sessionId, dir, payload);
      if (!state.created) state.created = now;
      if (typeof payload?.cwd === "string" && payload.cwd) state.cwd = payload.cwd;
      if (!state.agent && typeof payload?.agent_type === "string") state.agent = payload.agent_type;
      if (!state.model && typeof payload?.model === "string") state.model = modelFromTranscript(payload.model);
      if (!state.title && typeof payload?.session_title === "string" && payload.session_title) {
        state.title = payload.session_title.slice(0, 120);
      }
      if ((payload?.source === "resume" || payload?.source === "fork") && !state.resume) {
        const resume = {
          ...(Number.isFinite(payload?.context_tokens) ? { contextTokens: payload.context_tokens } : {}),
          ...(Number.isFinite(payload?.seconds_since_last_response) ? { secondsSinceLast: payload.seconds_since_last_response } : {}),
          ...(typeof payload?.prompt_cache_likely_expired === "boolean" ? { cacheExpired: payload.prompt_cache_likely_expired } : {}),
        };
        if (Object.keys(resume).length > 0) state.resume = resume;
      }
      persist(dir, sessionId, state);
      writeYAML(dir, sessionId, state);
      writeJSONL(dir, sessionId, {
        timestamp: now, sessionId, type: "session.start",
        source: payload?.source ?? null, model: payload?.model ?? null,
      });
      break;
    }
    case "UserPromptSubmit": {
      const { state } = hydrate(sessionId, dir, payload);
      const prompt = payload?.prompt ?? "";
      if (!state.created) {
        state.created = now;
        if (typeof payload?.cwd === "string" && payload.cwd) state.cwd = payload.cwd;
      }
      if (!state.turn) {
        state.turn = new Turn();
        state.turn.startTime = now;
      }
      if (state.turn.steps.length > 0) {
        completeTurnIfAny(dir, sessionId, state, "turn.complete");
        state.turn = new Turn();
        state.turn.startTime = now;
      }
      state.turn.userText = typeof prompt === "string" ? prompt : String(prompt ?? "");
      state.turn.userTime = now;
      if (!state.title && typeof prompt === "string" && prompt !== "") state.title = prompt.slice(0, 120);
      persist(dir, sessionId, state);
      writeYAML(dir, sessionId, state); // title lands in the header on first prompt
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "user.prompt", text: state.turn.userText.slice(0, 2000) });
      break;
    }
    case "PreToolUse": {
      const { state } = hydrate(sessionId, dir, payload);
      // Route subagent tool calls into the bracketed subagent turn.
      if (payload?.agent_id && state.subTurns[payload.agent_id]) state.activeSubagent = payload.agent_id;
      const tool = payload?.tool_name ?? "unknown";
      const input = payload?.tool_input ?? {};
      if (!state.created) state.created = now;
      const turn = ensureTurn(state, "", null);
      const step = turn.ensureStep(state.model);
      step.pendingTool = String(tool);
      try { step.pendingArgs = { ...(step.pendingArgs ?? {}), ...summarizeArgs(step.pendingTool, input) }; }
      catch { step.pendingArgs = {}; }
      step.pendingToolUseId = payload?.tool_use_id ?? null;
      persist(dir, sessionId, state);
      writeJSONL(dir, sessionId, {
        timestamp: now, sessionId, type: "tool.call", tool: step.pendingTool,
        toolUseId: payload?.tool_use_id ?? null, agentId: payload?.agent_id ?? state.activeSubagent,
      });
      break;
    }
    case "PostToolUse": {
      const { state } = hydrate(sessionId, dir, payload);
      if (payload?.agent_id && state.subTurns[payload.agent_id]) state.activeSubagent = payload.agent_id;
      const tool = payload?.tool_name ?? "unknown";
      const input = payload?.tool_input ?? {};
      if (!state.created) state.created = now;
      const turn = ensureTurn(state, "", null);
      const step = turn.ensureStep(state.model);
      const name = step.pendingTool ?? String(tool);
      let args = step.pendingArgs;
      if (args == null) args = summarizeArgs(name, input);
      step.toolCalls.push({
        tool: name,
        args,
        result: normalizeResult(payload?.tool_response ?? ""),
        ...(payload?.tool_use_id ? { toolUseId: payload.tool_use_id } : {}),
        ...(Number.isFinite(payload?.duration_ms) ? { durationMs: payload.duration_ms } : {}),
      });
      step.pendingTool = null;
      step.pendingArgs = null;
      step.pendingToolUseId = null;
      step.endTime = ts();
      writeJSONL(dir, sessionId, {
        timestamp: now, sessionId, type: "tool.result", tool: name,
        toolUseId: payload?.tool_use_id ?? null, durationMs: payload?.duration_ms ?? null,
      });
      writeYAML(dir, sessionId, state, { includePending: true });
      persist(dir, sessionId, state); // after writeYAML: captures pendingFile
      break;
    }
    case "PostToolUseFailure": {
      const { state } = hydrate(sessionId, dir, payload);
      if (payload?.agent_id && state.subTurns[payload.agent_id]) state.activeSubagent = payload.agent_id;
      const tool = payload?.tool_name ?? "unknown";
      if (!state.created) state.created = now;
      const turn = ensureTurn(state, "", null);
      const step = turn.ensureStep(state.model);
      const name = step.pendingTool ?? String(tool);
      const message = typeof payload?.error === "string" ? payload.error : "tool failed";
      step.toolCalls.push({
        tool: name,
        args: step.pendingArgs ?? summarizeArgs(name, payload?.tool_input ?? {}),
        result: `error: ${message}`,
        ...(payload?.tool_use_id ? { toolUseId: payload.tool_use_id } : {}),
        ...(Number.isFinite(payload?.duration_ms) ? { durationMs: payload.duration_ms } : {}),
      });
      step.pendingTool = null;
      step.pendingArgs = null;
      step.pendingToolUseId = null;
      step.endTime = ts();
      turn.error = message.slice(0, 500);
      if (payload?.is_interrupt) turn.interrupted = true;
      writeJSONL(dir, sessionId, {
        timestamp: now, sessionId, type: "tool.error", tool: name,
        error: message.slice(0, 500), isInterrupt: payload?.is_interrupt ?? null,
      });
      writeYAML(dir, sessionId, state, { includePending: true });
      persist(dir, sessionId, state);
      break;
    }
    case "PostToolBatch": {
      const { state } = hydrate(sessionId, dir, payload);
      if (!state.created) state.created = now;
      persist(dir, sessionId, state);
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "tool.batch" });
      break;
    }
    case "Stop": {
      const { state } = hydrate(sessionId, dir, payload);
      if (!state.created) state.created = now;
      if (state.activeSubagent) {
        completeSubTurnIfAny(dir, sessionId, state, state.activeSubagent);
        state.activeSubagent = null;
      }
      // last_assistant_message carries the final text directly — no
      // transcript race (prefer it over reading transcript_path here).
      if (state.turn) attachAssistantText(state.turn, state.model, payload?.last_assistant_message);
      completeTurnIfAny(dir, sessionId, state, "turn.complete");
      writeJSONL(dir, sessionId, {
        timestamp: now, sessionId, type: "turn.stop",
        stopHookActive: payload?.stop_hook_active ?? null,
        backgroundTasks: Array.isArray(payload?.background_tasks) ? payload.background_tasks.length : null,
      });
      break;
    }
    case "StopFailure": {
      const { state } = hydrate(sessionId, dir, payload);
      if (!state.created) state.created = now;
      if (state.turn) {
        if (typeof payload?.error === "string" && payload.error) state.turn.error = payload.error.slice(0, 500);
        attachAssistantText(state.turn, state.model, payload?.last_assistant_message);
      }
      completeTurnIfAny(dir, sessionId, state, "turn.failed");
      writeJSONL(dir, sessionId, {
        timestamp: now, sessionId, type: "turn.failed",
        error: typeof payload?.error === "string" ? payload.error.slice(0, 500) : null,
      });
      break;
    }
    case "SubagentStart": {
      const { state } = hydrate(sessionId, dir, payload);
      const agentId = payload?.agent_id ?? null;
      const agentType = payload?.agent_type ?? null;
      if (!state.created) state.created = now;
      if (agentId) {
        if (!state.subTurns[agentId]) {
          const t = new Turn();
          t.agent = { id: agentId, ...(agentType ? { type: agentType } : {}) };
          t.startTime = now;
          state.subTurns[agentId] = t;
        }
        state.activeSubagent = agentId;
      }
      persist(dir, sessionId, state);
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "subagent.start", agentId, agentType });
      break;
    }
    case "SubagentStop": {
      const { state } = hydrate(sessionId, dir, payload);
      const agentId = payload?.agent_id ?? null;
      if (!state.created) state.created = now;
      if (agentId) {
        const sub = state.subTurns[agentId];
        if (sub) {
          // Final text rides along — no transcript race for the subagent.
          attachAssistantText(sub, state.model, payload?.last_assistant_message);
          // Nested hybrid: the subagent's own transcript enriches its doc.
          const agentPath = payload?.agent_transcript_path;
          if (typeof agentPath === "string" && agentPath !== "") {
            try {
              const parsed = parseTranscriptFile(agentPath);
              if (parsed) {
                if (parsed.usage) sub.usage = parsed.usage;
                                if (parsed.model && !state.model) state.model = modelFromTranscript(parsed.model);
                sub.variables = [{ kind: "transcript", uri: agentPath }];
              }
            } catch { /* best effort only */ }
          }
        }
        completeSubTurnIfAny(dir, sessionId, state, agentId);
        if (state.activeSubagent === agentId) state.activeSubagent = null;
      }
      state.updated = ts();
      writeYAML(dir, sessionId, state);
      persist(dir, sessionId, state);
      writeJSONL(dir, sessionId, {
        timestamp: now, sessionId, type: "subagent.stop", agentId,
        stopHookActive: payload?.stop_hook_active ?? null,
        agentTranscriptPath: payload?.agent_transcript_path ?? null,
      });
      break;
    }
    case "PreCompact": {
      const { state } = hydrate(sessionId, dir, payload);
      state.compactedAt = now;
      persist(dir, sessionId, state);
      writeYAML(dir, sessionId, state);
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "session.compacted", phase: "pre", trigger: payload?.trigger ?? null });
      break;
    }
    case "PostCompact": {
      const { state } = hydrate(sessionId, dir, payload);
      persist(dir, sessionId, state);
      writeYAML(dir, sessionId, state);
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "session.compacted", phase: "post", trigger: payload?.trigger ?? null });
      break;
    }
    case "TaskCreated":
    case "TaskCompleted": {
      const { state } = hydrate(sessionId, dir, payload);
      if (!state.created) state.created = now;
      persist(dir, sessionId, state);
      writeJSONL(dir, sessionId, {
        timestamp: now, sessionId,
        type: event === "TaskCreated" ? "task.created" : "task.completed",
        subject: payload?.subject ?? payload?.task?.subject ?? null,
      });
      break;
    }
    case "PreModelSwitch":
    case "PostModelSwitch": {
      const { state } = hydrate(sessionId, dir, payload);
      if (!state.created) state.created = now;
      const to = payload?.to_model ?? payload?.model ?? null;
      if (event === "PostModelSwitch" && typeof to === "string" && to !== "") {
        state.model = modelFromTranscript(to);
      }
      persist(dir, sessionId, state);
      writeYAML(dir, sessionId, state);
      writeJSONL(dir, sessionId, {
        timestamp: now, sessionId, type: "model.switch", phase: event === "PreModelSwitch" ? "pre" : "post",
        from: payload?.from_model ?? null, to,
      });
      break;
    }
    case "SessionEnd": {
      const { state } = hydrate(sessionId, dir, payload);
      if (!state.created) state.created = now;
      // True session close (Cline/Copilot have no equivalent): flush any
      // open bracket and the live turn, then stamp the reason.
      if (state.activeSubagent) {
        completeSubTurnIfAny(dir, sessionId, state, state.activeSubagent);
        state.activeSubagent = null;
      }
      completeTurnIfAny(dir, sessionId, state, "turn.complete");
      if (typeof payload?.reason === "string" && payload.reason) state.endReason = payload.reason;
      state.updated = ts();
      writeYAML(dir, sessionId, state);
      persist(dir, sessionId, state);
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "session.end", reason: payload?.reason ?? null });
      break;
    }
    default: {
      // Unknown hook event: log + continue.
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "hook.unknown", hookEventName: event ?? null });
      break;
    }
  }
  // Best-effort transcript hybrid: enrich the header (model, git branch,
  // CLI version, usage rollup) and rewrite the canonical transcript view.
  // Self-contained (rehydrates from disk) so every hook type benefits
  // without touching the switch above.
  syncClaudeTranscript(dir, sessionId, payload);
}

// Read transcript_path when present and fold its envelope record into the
// header plus the canonical transcript.yaml. All best-effort: any failure
// is swallowed so the hook-driven log (the primary record) is never
// affected.
function syncClaudeTranscript(dir, sessionId, payload) {
  try {
    const transcriptPath = payload?.transcript_path;
    if (typeof transcriptPath !== "string" || transcriptPath === "") return;
    const { state } = hydrate(sessionId, dir, payload);
    const parsed = parseTranscriptFile(transcriptPath);
    if (!parsed) return;
    if (parsed.model && (!state.model || state.model.id === "unknown")) {
      state.model = modelFromTranscript(parsed.model);
    }
    if (parsed.gitBranch && !state.gitBranch) state.gitBranch = parsed.gitBranch;
    if (parsed.claudeVersion && !state.claudeVersion) state.claudeVersion = parsed.claudeVersion;
    if (!state.title && parsed.title) state.title = parsed.title;
    if (parsed.usage) {
      // The transcript is cumulative: take running maxima (monotonic).
      const prev = state.usage ?? {};
      const usage = {};
      for (const [k, v] of Object.entries(parsed.usage)) {
        usage[k] = Math.max(prev[k] ?? 0, v ?? 0) || null;
      }
      for (const [k, v] of Object.entries(prev)) {
        if (!(k in usage) && v != null) usage[k] = v;
      }
      state.usage = Object.values(usage).every((v) => v == null) ? null : usage;
    }
    if (parsed.docs) {
      writeTranscriptYaml(dir, parsed.docs);
      if (parsed.docs.length !== (state.transcriptTurns ?? -1)) {
        writeJSONL(dir, sessionId, { timestamp: ts(), sessionId, type: "transcript.sync", turns: parsed.docs.length });
      }
      state.transcriptTurns = parsed.docs.length;
    }
    state.updated = ts();
    writeYAML(dir, sessionId, state);
    persist(dir, sessionId, state);
  } catch { /* best effort only */ }
}

export async function run() {
  // Silent-logger contract: stdout stays EMPTY, exit 0. (Only
  // UserPromptSubmit/SessionStart/PostModelSwitch stdout reaches the
  // transcript, so printing nothing keeps us out of Claude's context.)
  try {
    const raw = await readStdin();
    const payload = raw.trim() ? JSON.parse(raw) : {};
    await handle(payload);
  } catch (err) {
    // Fail-open, but leave a trace. stdout stays empty.
    const msg = `[${new Date().toISOString()}] router: ${err?.stack ?? err}\n`;
    try {
      const home = process.env.HOME ?? "";
      if (home) appendFileSync(join(home, ".claude-hook-errors.log"), msg);
    } catch { /* ignore */ }
    try {
      const p = JSON.parse(raw || "{}");
      const root = typeof p.cwd === "string" && p.cwd ? p.cwd : null;
      if (root) {
        mkdirSync(join(root, ".claude", "run-logs"), { recursive: true });
        appendFileSync(join(root, ".claude", "run-logs", "hook-errors.log"), msg);
      }
    } catch { /* ignore */ }
  }
}
