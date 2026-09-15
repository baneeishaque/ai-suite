// File IO for the Claude hooks logger. All paths resolve under
// <workspace>/.claude/run-logs/<sessionId>/ (workspace = hook cwd,
// else process.cwd()). Atomic appends for JSONL, atomic
// per-turn writes for YAML. No read-modify-write on turn files.
import { appendFileSync, existsSync, mkdirSync, readFileSync, readdirSync, unlinkSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { dump, loadAll } from "js-yaml";
import { buildDocs, ts } from "./core.js";

export const RUN_LOGS_DIR = join(".claude", "run-logs");

export function sanitizeTaskId(taskId) {
  return String(taskId ?? "unknown").replace(/[^a-zA-Z0-9-_]/g, "_").slice(0, 128) || "unknown";
}

export function sanitizeFileSegment(iso) {
  return String(iso ?? ts()).replace(/[:.]/g, "-");
}

export function resolveBase(workspaceRoots) {
  const root = Array.isArray(workspaceRoots) && workspaceRoots[0]
    ? workspaceRoots[0]
    : process.cwd();
  return join(root, RUN_LOGS_DIR);
}

export function taskDir(base, taskId) {
  const dir = join(base, sanitizeTaskId(taskId));
  mkdirSync(dir, { recursive: true });
  return dir;
}

export function statePath(dir) {
  return join(dir, "state.json");
}

// Persisted state shape (state.json): header fields + the live in-flight
// turn as plain JSON. Hooks run as separate processes with no shared memory,
// so the live turn MUST round-trip through disk or Pre/PostToolUse pairs
// (separate invocations) lose the pending tool and user text.
export function serializeTurn(turn) {
  if (!turn) return null;
  return {
    userText: turn.userText,
    userTime: turn.userTime,
    agent: turn.agent,
    uuid: turn.uuid,
    parentUuid: turn.parentUuid,
    result: turn.result,
    error: turn.error,
    interrupted: turn.interrupted,
    usage: turn.usage,
    timings: turn.timings,
    variables: turn.variables,
    startTime: turn.startTime,
    steps: turn.steps.map((s) => ({
      model: s.model,
      agent: s.agent,
      thinking: s.thinking,
      thinkingStartTime: s.thinkingStartTime,
      thinkingDuration: s.thinkingDuration,
      responseText: s.responseText,
      toolCalls: s.toolCalls,
      startTime: s.startTime,
      endTime: s.endTime,
      pendingTool: s.pendingTool,
      pendingArgs: s.pendingArgs,
    })),
  };
}

// Back-compat alias (earlier forks named this serializeLiveTurn).
export const serializeLiveTurn = serializeTurn;

export function serializeSubTurns(subTurns) {
  const out = {};
  for (const [id, turn] of Object.entries(subTurns ?? {})) out[id] = serializeTurn(turn);
  return out;
}

export function loadPersisted(dir) {
  try {
    if (!existsSync(statePath(dir))) return null;
    return JSON.parse(readFileSync(statePath(dir), "utf-8"));
  } catch { return null; }
}

export function savePersisted(dir, persisted) {
  writeFileSync(statePath(dir), JSON.stringify(persisted, null, 2));
}

export function writeJSONL(dir, taskId, entry) {
  const f = join(dir, `${sanitizeTaskId(taskId)}.jsonl`);
  appendFileSync(f, JSON.stringify(entry) + "\n");
}

export function writeTurnsJSONL(dir, taskId, turnDoc, turnIndex) {
  const f = join(dir, `${sanitizeTaskId(taskId)}.turns.jsonl`);
  appendFileSync(f, JSON.stringify({ turnIndex, ...turnDoc }) + "\n");
}

// Rebuild persisted turns list from numbered turn files + header (resume path).
// Completed files match ^\d{3}-(?!pending-).*\.yaml; pending files are ignored
// here (they are rewritten, never promoted — fixes the opencode v2 orphan bug).
export function loadTurnsFromDisk(dir) {
  if (!existsSync(dir)) return { turns: [], header: null };
  const files = readdirSync(dir)
    .filter((f) => /^\d{3}-(?!pending-|header-).*\.yaml$/.test(f))
    .sort();
  const turns = [];
  let header = null;
  for (const f of files) {
    try {
      const docs = loadAll(readFileSync(join(dir, f), "utf-8"));
      for (const d of docs) {
        if (!d || typeof d !== "object") continue;
        if (d.session && !header && f.startsWith("000-")) header = d;
        else if (d.user) turns.push(d);
      }
    } catch { /* skip bad file */ }
  }
  return { turns, header };
}

function headerFileName(created) {
  return `000-header-${sanitizeFileSegment(created)}.yaml`;
}

function turnFileName(index, endTime, pending) {
  const n = String(index).padStart(3, "0");
  if (pending) return `${n}-pending-${sanitizeFileSegment(endTime ?? ts())}.yaml`;
  return `${n}-${sanitizeFileSegment(endTime ?? ts())}.yaml`;
}

// Write header (once) + any unwritten completed turns. When includePending is
// true and a live turn has tool content, also (over)write the pending file so
// a crash never loses the last tool call (TaskComplete/Cancel finalizes it).
export function writeYAML(dir, taskId, state, opts = {}) {
  const { includePending = false } = opts;
  mkdirSync(dir, { recursive: true });

  if (!existsSync(join(dir, headerFileName(state.created ?? ts())))) {
    const existing = existsSync(dir) ? readdirSync(dir).filter((f) => f.startsWith("000-header-")) : [];
    if (existing.length === 0) {
      const [header] = buildDocs(state, taskId);
      writeFileSync(join(dir, headerFileName(state.created ?? ts())), `---\n${dump(header)}`);
    }
  } else if (state.turns.length === 0) {
    // header exists, nothing else to do
  }

  // Rewrite header when model/title/compacted changed (cheap, idempotent).
  try {
    const [header] = buildDocs(state, taskId);
    const headers = readdirSync(dir).filter((f) => f.startsWith("000-header-"));
    const target = headers[0] ?? headerFileName(state.created ?? ts());
    writeFileSync(join(dir, target), `---\n${dump(header)}`);
  } catch { /* best effort */ }

  const startIdx = state.writtenTurns;
  for (let i = startIdx; i < state.turns.length; i++) {
    const doc = state.turns[i];
    const fname = turnFileName(i + 1, ts(), false);
    writeFileSync(join(dir, fname), `---\n${dump(doc)}`);
  }
  state.writtenTurns = state.turns.length;
  // Delete ONLY our own tracked pending file when its turn finalized.
  // Orphan pending files from crashed sessions are evidence: never promoted,
  // never deleted here.
  if (state.pendingFile) {
    try { unlinkSync(join(dir, state.pendingFile)); } catch { /* already gone */ }
    state.pendingFile = null;
  }

  if (includePending && state.turn && state.turn.steps.length > 0) {
    const pendingDoc = state.turn.toFields();
    const hasTools = (pendingDoc.assistant ?? []).some((s) => s.tool_calls?.length > 0);
    if (hasTools) {
      const fname = turnFileName(state.turns.length + 1, ts(), true);
      if (state.pendingFile && state.pendingFile !== fname) {
        try { unlinkSync(join(dir, state.pendingFile)); } catch { /* already gone */ }
      }
      writeFileSync(join(dir, fname), `---\n${dump(pendingDoc)}`);
      state.pendingFile = fname;
    }
  }
}
