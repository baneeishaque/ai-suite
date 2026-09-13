// Cline hooks router: reads one JSON payload from stdin, dispatches by
// hookName, appends to .cline/run-logs/<taskId>/. Always prints
// {"cancel":false} (fail-open: the logger must never block the agent).
import { loadPersisted, resolveBase, savePersisted, loadTurnsFromDisk, sanitizeTaskId, serializeLiveTurn, taskDir, writeJSONL, writeTurnsJSONL, writeYAML } from "./io.js";
import { Turn, finalizeTurn, modelFromHook, newSessionState, normalizeResult, reviveLiveTurn, ts } from "./core.js";
import { appendFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

function readStdin() {
  return new Promise((resolve) => {
    let data = "";
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (c) => { data += c; });
    process.stdin.on("end", () => resolve(data));
    // Cline may keep stdin open briefly; bound the wait.
    setTimeout(() => resolve(data), 5000);
  });
}

function hookTs(payload) {
  const n = Number(payload?.timestamp);
  if (Number.isFinite(n) && n > 0) return new Date(n).toISOString();
  return ts();
}

function hydrate(taskId, dir, payload) {
  // Rebuild state from disk on every invocation (hooks are separate
  // processes; no in-memory state survives). Live Turn is recreated empty;
  // completed turns + header come from numbered YAML files.
  const persisted = loadPersisted(dir) ?? {};
  const { turns, header } = loadTurnsFromDisk(dir);
  const state = newSessionState();
  state.turns = turns;
  state.writtenTurns = turns.length;
  state.created = persisted.created ?? header?.session?.created ?? hookTs(payload);
  state.updated = persisted.updated ?? null;
  state.model = persisted.model ?? modelFromHook(payload?.model) ?? header?.model ?? null;
  state.title = persisted.title ?? header?.title ?? null;
  state.compactedAt = persisted.compactedAt ?? null;
  state.pendingFile = persisted.pendingFile ?? null;
  // Live turn survives across hook processes via state.json.
  state.turn = reviveLiveTurn(persisted.liveTurn ?? null);
  return { state, persisted };
}

function persist(dir, taskId, state) {
  savePersisted(dir, {
    created: state.created,
    updated: state.updated,
    model: state.model,
    title: state.title,
    compactedAt: state.compactedAt,
    writtenTurns: state.writtenTurns,
    pendingFile: state.pendingFile,
    liveTurn: serializeLiveTurn(state.turn),
  });
  void taskId;
}

function ensureTurn(state, userText, userTime, model) {
  if (!state.turn) {
    state.turn = new Turn();
    state.turn.userText = userText ?? "";
    state.turn.userTime = userTime ?? null;
    state.turn.startTime = ts();
  } else if (userText != null && state.turn.userText === "") {
    state.turn.userText = userText;
    state.turn.userTime = userTime ?? state.turn.userTime;
  }
  if (model && !state.model) state.model = model;
  return state.turn;
}

function completeTurnIfAny(dir, taskId, state, type) {
  if (finalizeTurn(state)) {
    const idx = state.turns.length - 1;
    writeJSONL(dir, taskId, { timestamp: ts(), taskId, type, turnIndex: idx });
    writeTurnsJSONL(dir, taskId, state.turns[idx], idx);
  }
  state.updated = ts();
  writeYAML(dir, taskId, state);
  persist(dir, taskId, state);
}

export async function handle(payload) {
  const taskId = sanitizeTaskId(payload?.taskId ?? payload?.taskStart?.taskMetadata?.taskId);
  const base = resolveBase(payload?.workspaceRoots);
  const dir = taskDir(base, taskId);
  const now = hookTs(payload);
  const model = modelFromHook(payload?.model);
  const hook = payload?.hookName;

  switch (hook) {
    case "TaskStart": {
      const { state } = hydrate(taskId, dir, payload);
      const task = payload?.taskStart?.task ?? payload?.taskStart?.taskMetadata?.initialTask ?? "";
      if (!state.created) state.created = now;
      if (model) state.model = model;
      if (!state.title && typeof task === "string") state.title = task.slice(0, 120) || null;
      persist(dir, taskId, state);
      writeYAML(dir, taskId, state);
      writeJSONL(dir, taskId, { timestamp: now, taskId, type: "task.start", model: state.model, title: state.title });
      break;
    }
    case "TaskResume": {
      const { state } = hydrate(taskId, dir, payload);
      if (!state.created) {
        state.created = now;
        if (model) state.model = model;
        persist(dir, taskId, state);
        writeYAML(dir, taskId, state);
      }
      writeJSONL(dir, taskId, { timestamp: now, taskId, type: "task.resume" });
      break;
    }
    case "UserPromptSubmit": {
      const { state } = hydrate(taskId, dir, payload);
      const prompt = payload?.userPromptSubmit?.prompt ?? "";
      if (!state.created) {
        state.created = now;
        if (model) state.model = model;
      }
      // Restore in-flight turn text from the last pending file when the
      // prompt arrives in a fresh process (multi-process turn continuity).
      if (!state.turn) {
        state.turn = new Turn();
        state.turn.startTime = now;
      }
      if (state.turn.steps.length > 0) {
        completeTurnIfAny(dir, taskId, state, "turn.complete");
        state.turn = new Turn();
        state.turn.startTime = now;
      }
      state.turn.userText = typeof prompt === "string" ? prompt : String(prompt ?? "");
      state.turn.userTime = now;
      if (model) state.model = model;
      persist(dir, taskId, state);
      writeJSONL(dir, taskId, { timestamp: now, taskId, type: "user.prompt", text: state.turn.userText.slice(0, 2000) });
      break;
    }
    case "PreToolUse": {
      const { state } = hydrate(taskId, dir, payload);
      const tool = payload?.preToolUse?.tool ?? "unknown";
      const params = payload?.preToolUse?.parameters ?? {};
      if (!state.created) {
        state.created = now;
        if (model) state.model = model;
      }
      const turn = ensureTurn(state, "", null, model);
      const step = turn.ensureStep(state.model);
      step.pendingTool = String(tool);
      try { step.pendingArgs = typeof params === "object" ? params : { value: params }; }
      catch { step.pendingArgs = {}; }
      persist(dir, taskId, state);
      writeJSONL(dir, taskId, { timestamp: now, taskId, type: "tool.call", tool: step.pendingTool, args: step.pendingArgs });
      break;
    }
    case "PostToolUse": {
      const { state } = hydrate(taskId, dir, payload);
      const pu = payload?.postToolUse ?? {};
      const tool = pu.tool ?? "unknown";
      const params = pu.parameters ?? {};
      const ok = pu.success !== false;
      if (!state.created) {
        state.created = now;
        if (model) state.model = model;
      }
      // Recover the pending tool name from the last pending YAML when this
      // hook runs in a fresh process (common: Pre and Post are separate
      // invocations with no shared memory).
      const turn = ensureTurn(state, "", null, model);
      const step = turn.ensureStep(state.model);
      const name = step.pendingTool ?? String(tool);
      let args = step.pendingArgs;
      if (args == null) {
        try { args = typeof params === "object" ? params : { value: params }; }
        catch { args = {}; }
      }
      step.toolCalls.push({
        tool: name,
        args,
        result: ok ? normalizeResult(pu.result ?? "") : `ERROR: ${normalizeResult(pu.result ?? "failed")}`,
      });
      step.pendingTool = null;
      step.pendingArgs = null;
      step.endTime = ts();
      writeJSONL(dir, taskId, {
        timestamp: now, taskId, type: "tool.result", tool: name,
        success: ok, durationMs: pu.durationMs ?? null,
      });
      writeYAML(dir, taskId, state, { includePending: true });
      persist(dir, taskId, state); // after writeYAML: captures pendingFile
      break;
    }
    case "TaskComplete":
    case "TaskCancel":
    case "TaskComplete_blocked": {
      const { state } = hydrate(taskId, dir, payload);
      if (!state.created) {
        state.created = now;
        if (model) state.model = model;
      }
      completeTurnIfAny(dir, taskId, state, "turn.complete");
      writeJSONL(dir, taskId, { timestamp: now, taskId, type: hook === "TaskCancel" ? "task.cancel" : "task.complete" });
      break;
    }
    case "PreCompact": {
      const { state } = hydrate(taskId, dir, payload);
      state.compactedAt = now;
      persist(dir, taskId, state);
      writeYAML(dir, taskId, state);
      writeJSONL(dir, taskId, {
        timestamp: now, taskId, type: "task.compacted",
        conversationLength: payload?.preCompact?.conversationLength ?? null,
        estimatedTokens: payload?.preCompact?.estimatedTokens ?? null,
      });
      break;
    }
    default: {
      // Unknown hook (e.g. future TaskError/SessionShutdown): log + continue.
      writeJSONL(dir, taskId, { timestamp: now, taskId, type: "hook.unknown", hookName: hook ?? null });
      break;
    }
  }
}

export async function run() {
  let raw = "";
  try {
    raw = await readStdin();
    const payload = raw.trim() ? JSON.parse(raw) : {};
    await handle(payload);
  } catch (err) {
    // Fail-open, but leave a trace: HOME-global log always, workspace log
    // when the payload reveals the workspace root. stdout stays pure JSON.
    const msg = `[${new Date().toISOString()}] router: ${err?.stack ?? err}\n`;
    try {
      const home = process.env.HOME ?? "";
      if (home) appendFileSync(join(home, ".cline-hook-errors.log"), msg);
    } catch { /* ignore */ }
    try {
      const p = JSON.parse(raw || "{}");
      const root = Array.isArray(p.workspaceRoots) && p.workspaceRoots[0];
      if (root) {
        mkdirSync(join(root, ".cline", "run-logs"), { recursive: true });
        appendFileSync(join(root, ".cline", "run-logs", "hook-errors.log"), msg);
      }
    } catch { /* ignore */ }
  }
  process.stdout.write(JSON.stringify({ cancel: false }));
}
