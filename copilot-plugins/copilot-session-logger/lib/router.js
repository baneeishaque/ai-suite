// Copilot hooks router: reads one JSON payload from stdin, dispatches by
// hook_event_name, appends to .copilot/run-logs/<sessionId>/. Always prints
// {"continue":true} (fail-open: the logger must never block the agent).
import { loadPersisted, resolveBase, savePersisted, loadTurnsFromDisk, sanitizeTaskId, serializeSubTurns, serializeTurn, taskDir, writeJSONL, writeTurnsJSONL, writeYAML } from "./io.js";
import { Turn, finalizeTurn, modelFromTranscript, newSessionState, normalizeResult, reviveTurn, ts } from "./core.js";
import { parseTranscriptFile, writeTranscriptYaml } from "./copilot-transcript.js";
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
  // Copilot timestamps are ISO-8601 strings (unlike Cline ms-strings).
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
  state.compactedAt = persisted.compactedAt ?? null;
  state.pendingFile = persisted.pendingFile ?? null;
  state.transcriptTurns = persisted.transcriptTurns ?? null;
  state.usage = persisted.usage ?? header?.usage ?? null;
  state.producer = persisted.producer ?? header?.session?.producer ?? null;
  state.copilotVersion = persisted.copilotVersion ?? header?.session?.copilot_version ?? null;
  state.vscodeVersion = persisted.vscodeVersion ?? header?.session?.vscode_version ?? null;
  state.gitBranch = persisted.gitBranch ?? header?.session?.git_branch ?? null;
  state.repo = persisted.repo ?? header?.session?.repository ?? null;
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
    compactedAt: state.compactedAt,
    writtenTurns: state.writtenTurns,
    pendingFile: state.pendingFile,
    transcriptTurns: state.transcriptTurns,
    usage: state.usage,
    producer: state.producer,
    copilotVersion: state.copilotVersion,
    vscodeVersion: state.vscodeVersion,
    gitBranch: state.gitBranch,
    repo: state.repo,
    activeSubagent: state.activeSubagent,
    liveTurn: serializeTurn(state.turn),
    subTurns: serializeSubTurns(state.subTurns),
  });
  void sessionId;
}

// The live turn tool calls belong to: the bracketed subagent turn when a
// SubagentStart..Stop bracket is open, else the main turn.
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

// Per-tool argument summarizers for the known Copilot inventory (see
// extensions/copilot/src/extension/tools/node in microsoft/vscode).
// Unknown tools fall back to a capped raw dump. Keeps YAML skimable.
const ARG_SUMMARIZERS = {
  copilot_readFile: (i) => ({ path: i?.filePath ?? i?.path ?? null }),
  copilot_createFile: (i) => ({ path: i?.filePath ?? i?.path ?? null }),
  copilot_applyPatch: (i) => ({ path: i?.filePath ?? i?.path ?? null }),
  copilot_multiReplaceString: (i) => ({ path: i?.filePath ?? i?.path ?? null }),
  copilot_getErrors: (i) => ({ uris: i?.uris ?? i?.files ?? null }),
  copilot_findTextInFiles: (i) => ({ query: i?.query ?? i?.pattern ?? null, files: i?.filesToInclude ?? null }),
  copilot_findFiles: (i) => ({ query: i?.query ?? i?.pattern ?? null }),
  copilot_listDirectory: (i) => ({ path: i?.path ?? i?.directory ?? null }),
  run_in_terminal: (i) => ({ command: typeof i?.command === "string" ? i.command.slice(0, 2000) : null }),
  get_terminal_output: (i) => ({ terminalId: i?.terminalId ?? null }),
  kill_terminal: (i) => ({ terminalId: i?.terminalId ?? null }),
};

function summarizeArgs(toolName, input) {
  try {
    if (!input || typeof input !== "object") return {};
    const fn = ARG_SUMMARIZERS[toolName];
    if (fn) {
      const out = fn(input) ?? {};
      return Object.fromEntries(Object.entries(out).filter(([, v]) => v != null));
    }
    const raw = JSON.stringify(input);
    return { _raw: raw.length > 2000 ? raw.slice(0, 2000) : raw };
  } catch { return {}; }
}

export async function handle(payload) {
  const sessionId = sanitizeTaskId(payload?.session_id ?? "unknown");
  const base = resolveBase([payload?.cwd]);
  const dir = taskDir(base, sessionId);
  // Raw payload capture: Copilot payload shapes drift from the docs;
  // this log grounds future mapping.
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
      // CLI sessions lead with initial_prompt on SessionStart.
      if (!state.title && typeof payload?.initial_prompt === "string" && payload.initial_prompt !== "") {
        state.title = payload.initial_prompt.slice(0, 120);
      }
      persist(dir, sessionId, state);
      writeYAML(dir, sessionId, state);
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "session.start", source: payload?.source ?? null, model: payload?.model ?? null });
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
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "tool.call", tool: step.pendingTool, toolUseId: payload?.tool_use_id ?? null });
      break;
    }
    case "PostToolUse": {
      const { state } = hydrate(sessionId, dir, payload);
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
      });
      step.pendingTool = null;
      step.pendingArgs = null;
      step.pendingToolUseId = null;
      step.endTime = ts();
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "tool.result", tool: name, toolUseId: payload?.tool_use_id ?? null });
      writeYAML(dir, sessionId, state, { includePending: true });
      persist(dir, sessionId, state); // after writeYAML: captures pendingFile
      break;
    }
    case "PreCompact": {
      const { state } = hydrate(sessionId, dir, payload);
      state.compactedAt = now;
      persist(dir, sessionId, state);
      writeYAML(dir, sessionId, state);
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "session.compacted", trigger: payload?.trigger ?? null });
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
        completeSubTurnIfAny(dir, sessionId, state, agentId);
        if (state.activeSubagent === agentId) state.activeSubagent = null;
      }
      state.updated = ts();
      writeYAML(dir, sessionId, state);
      persist(dir, sessionId, state);
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "subagent.stop", agentId, stopHookActive: payload?.stop_hook_active ?? null });
      break;
    }
    case "Stop": {
      const { state } = hydrate(sessionId, dir, payload);
      if (!state.created) state.created = now;
      // Flush any still-open subagent bracket first (nested doc lands
      // before the parent turn that follows it).
      if (state.activeSubagent) {
        completeSubTurnIfAny(dir, sessionId, state, state.activeSubagent);
        state.activeSubagent = null;
      }
      backfillStopResponse(state, payload);
      if (!state.turn || state.turn.steps.length === 0) {
        // Nothing to complete (and no backfilled answer): keep the live
        // turn so a later Stop can still backfill it once the transcript
        // flush lands. finalizeTurn would drop it.
        state.updated = ts();
        writeYAML(dir, sessionId, state);
        persist(dir, sessionId, state);
      } else {
        completeTurnIfAny(dir, sessionId, state, "turn.complete");
      }
      writeJSONL(dir, sessionId, {
        timestamp: now, sessionId, type: "session.stop",
        stopHookActive: payload?.stop_hook_active ?? null, stopReason: payload?.stop_reason ?? null,
      });
      break;
    }
    default: {
      // Unknown hook event: log + continue.
      writeJSONL(dir, sessionId, { timestamp: now, sessionId, type: "hook.unknown", hookEventName: event ?? null });
      break;
    }
  }
  // Best-effort transcript hybrid: enrich the header (actual model,
  // usage rollup, agent/mode) and rewrite the canonical transcript view.
  // Self-contained (rehydrates from disk) so every hook type benefits
  // without touching the switch above.
  syncCopilotTranscript(dir, sessionId, payload);
}

function lastMatchingPair(parsed, userText) {
  const pair = parsed?.lastPair;
  if (!pair || pair.userText.trim() !== userText.trim()) return null;
  return pair;
}

// Stop-time backfill: tool-less turns (user text, no steps — e.g. a ping)
// would otherwise vanish. When the transcript's last Q/A pair matches the
// live turn's prompt, attach the assistant text so the turn is recorded.
function backfillStopResponse(state, payload) {
  try {
    const turn = state.turn;
    if (!turn || turn.steps.length > 0) return;
    if (typeof turn.userText !== "string" || turn.userText.trim() === "") return;
    const transcriptPath = payload?.transcript_path;
    if (typeof transcriptPath !== "string" || transcriptPath === "") return;
    // The transcript lags the hook (async flush): one bounded re-read when
    // the first parse has no matching pair yet (the CLI ping proved the race).
    let pair = lastMatchingPair(parseTranscriptFile(transcriptPath), turn.userText);
    if (!pair) {
      try {
        Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 1000);
      } catch { /* ignore */ }
      pair = lastMatchingPair(parseTranscriptFile(transcriptPath), turn.userText);
    }
    if (!pair) return;
    if (typeof pair.assistantText !== "string" || pair.assistantText === "") return;
    // NOTE: Step stores text as arrays (no setThinkingResponse here).
    turn.ensureStep(state.model).responseText.push(pair.assistantText);
  } catch { /* best effort only */ }
}

// Read transcript_path when present and fold its record into the header
// (versions, actual model, title, usage rollup) plus the canonical
// transcript.yaml. All best-effort: any failure is swallowed so the
// hook-driven log (the primary record) is never affected.
function syncCopilotTranscript(dir, sessionId, payload) {
  try {
    const transcriptPath = payload?.transcript_path;
    if (typeof transcriptPath !== "string" || transcriptPath === "") return;
    const { state } = hydrate(sessionId, dir, payload);
    const parsed = parseTranscriptFile(transcriptPath);
    if (!parsed) return;
    if (parsed.provenance) {
      if (parsed.provenance.producer && !state.producer) state.producer = parsed.provenance.producer;
      if (parsed.provenance.copilotVersion && !state.copilotVersion) state.copilotVersion = parsed.provenance.copilotVersion;
      if (parsed.provenance.vscodeVersion && !state.vscodeVersion) state.vscodeVersion = parsed.provenance.vscodeVersion;
      if (parsed.provenance.branch && !state.gitBranch) state.gitBranch = parsed.provenance.branch;
      if (parsed.provenance.repository && !state.repo) state.repo = parsed.provenance.repository;
    }
    if (parsed.model && !state.model) state.model = modelFromTranscript(parsed.model);
    else if (parsed.model && state.model?.id === "unknown") state.model = modelFromTranscript(parsed.model);
    if (parsed.agent && !state.agent) state.agent = parsed.agent;
    if (parsed.mode && !state.mode) state.mode = parsed.mode;
    if (!state.title && parsed.title) state.title = parsed.title;
    if (parsed.usage) {
      // The transcript is cumulative: take running maxima (monotonic).
      // CLI streams contribute outputTokens/inputTokens/nanoAiu/
      // premiumRequests; exports contribute prompt/completion/credits.
      const prev = state.usage ?? {};
      const usage = {};
      for (const k of ["promptTokens", "completionTokens", "copilotCredits", "outputTokens", "inputTokens", "nanoAiu", "premiumRequests"]) {
        const v = Math.max(prev[k] ?? 0, parsed.usage[k] ?? 0) || null;
        if (v != null) usage[k] = v;
      }
      state.usage = Object.keys(usage).length > 0 ? usage : null;
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
  let raw = "";
  try {
    raw = await readStdin();
    const payload = raw.trim() ? JSON.parse(raw) : {};
    await handle(payload);
  } catch (err) {
    // Fail-open, but leave a trace. stdout stays pure JSON.
    const msg = `[${new Date().toISOString()}] router: ${err?.stack ?? err}\n`;
    try {
      const home = process.env.HOME ?? "";
      if (home) appendFileSync(join(home, ".copilot-hook-errors.log"), msg);
    } catch { /* ignore */ }
    try {
      const p = JSON.parse(raw || "{}");
      const root = typeof p.cwd === "string" && p.cwd ? p.cwd : null;
      if (root) {
        mkdirSync(join(root, ".copilot", "run-logs"), { recursive: true });
        appendFileSync(join(root, ".copilot", "run-logs", "hook-errors.log"), msg);
      }
    } catch { /* ignore */ }
  }
  process.stdout.write(JSON.stringify({ continue: true }));
}
