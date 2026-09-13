// Bridge to Cline's own on-disk session store (~/.cline/data/sessions).
// The hook payload's taskId (conv_<ts>_<rand>) differs from Cline's session
// id, so sessions are discovered by workspace + timestamp proximity and the
// mapping is cached in state.json. All functions are best-effort and return
// null/empty on any failure — the hook-driven log must never break.
import { existsSync, mkdirSync, readdirSync, readFileSync, renameSync, statSync, unlinkSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { dump } from "js-yaml";
import { formatLocal } from "./core.js";

export function sessionsRoot() {
  if (process.env.CLINE_SESSIONS_ROOT) return process.env.CLINE_SESSIONS_ROOT;
  const home = process.env.HOME ?? "";
  return home ? join(home, ".cline", "data", "sessions") : "";
}

export function parseConvTs(taskId) {
  const m = String(taskId ?? "").match(/conv_(\d+)_/);
  const n = m ? Number(m[1]) : NaN;
  return Number.isFinite(n) && n > 0 ? n : null;
}

function readJsonFile(path) {
  try {
    return JSON.parse(readFileSync(path, "utf-8"));
  } catch { return null; }
}

// Resolve the Cline session dir for a hook taskId. Cached mapping wins when
// the dir still exists; otherwise scan newest-first (bounded) for a session
// whose workspace matches and whose transcript holds a user message near the
// conversation timestamp embedded in the taskId.
export function resolveSession(taskId, workspaceRoot, cached) {
  if (cached?.sessionPath && existsSync(cached.sessionPath)) {
    return { sessionId: cached.sessionId ?? null, sessionPath: cached.sessionPath };
  }
  const root = sessionsRoot();
  if (!root || !existsSync(root)) return null;
  const convTs = parseConvTs(taskId);
  let dirs;
  try {
    dirs = readdirSync(root)
      .map((d) => ({ d, p: join(root, d) }))
      .filter(({ p }) => { try { return statSync(p).isDirectory(); } catch { return false; } })
      .map(({ d, p }) => ({ d, p, mtime: safeMtime(p) }))
      .sort((a, b) => b.mtime - a.mtime)
      .slice(0, 60);
  } catch { return null; }
  for (const { d, p } of dirs) {
    const meta = readJsonFile(join(p, `${d}.json`));
    if (!meta) continue;
    if (workspaceRoot) {
      const ws = meta.workspace_root ?? meta.cwd ?? "";
      if (ws && ws !== workspaceRoot) continue;
    }
    if (convTs == null) {
      // No conversation timestamp: accept the newest session for this
      // workspace started within the last 15 minutes.
      const started = Date.parse(meta.started_at ?? "") || 0;
      if (Date.now() - started < 15 * 60 * 1000) {
        return { sessionId: meta.session_id ?? d, sessionPath: p };
      }
      continue;
    }
    const transcript = readJsonFile(join(p, `${d}.messages.json`));
    const msgs = transcript?.messages ?? (Array.isArray(transcript) ? transcript : null);
    if (!Array.isArray(msgs)) continue;
    const hit = msgs.some((m) => m?.role === "user"
      && hasUserText(m)
      && Math.abs(Number(m.ts) - convTs) < 30000);
    if (hit) return { sessionId: meta.session_id ?? d, sessionPath: p };
  }
  return null;
}

function safeMtime(p) {
  try { return statSync(p).mtimeMs; } catch { return 0; }
}

function hasUserText(m) {
  return (m.content ?? []).some((c) => c?.type !== "tool_result"
    && (typeof c?.text === "string" || typeof c?.content === "string" || c?.type === "text"));
}

export function readSessionMeta(sessionPath, sessionId) {
  const base = sessionId ?? String(sessionPath).split("/").pop();
  return readJsonFile(join(sessionPath, `${base}.json`));
}

// Load + parse the transcript and return canonical turn docs, or null when
// unavailable (missing files, bad JSON, empty transcript).
export function loadTranscriptDocs(sessionPath, sessionId) {
  try {
    const base = sessionId ?? String(sessionPath).split("/").pop();
    const raw = readFileSync(join(sessionPath, `${base}.messages.json`), "utf-8");
    const data = JSON.parse(raw);
    const messages = Array.isArray(data) ? data : data?.messages ?? null;
    if (!Array.isArray(messages) || messages.length === 0) return null;
    const docs = transcriptTurnDocs(parseTranscript(messages));
    return docs.length > 0 ? docs : null;
  } catch { return null; }
}

export function stripUserTags(text) {
  return String(text ?? "")
    .replace(/<user_input[^>]*>/g, "")
    .replace(/<\/user_input>/g, "")
    .trim();
}

function blockText(c) {
  if (typeof c?.text === "string") return c.text;
  if (typeof c?.content === "string") return c.content;
  return "";
}

// Parse a Cline messages transcript into turns. A role=user message carrying
// non-tool_result content opens a new turn; tool_result-only user messages
// attach to the current turn (matched to tool calls by tool_use_id, FIFO
// fallback). Consecutive assistant messages in one turn become steps.
export function parseTranscript(messages) {
  const turns = [];
  let current = null;
  const newTurn = (text, ts) => {
    current = { userText: text, userTime: ts ?? null, steps: [] };
    turns.push(current);
    return current;
  };
  const curStep = () => {
    if (!current) newTurn("", null);
    let s = current.steps[current.steps.length - 1];
    if (!s || s.closed) {
      s = { thinking: [], response: [], toolCalls: [], start: null, end: null, tokens: null, closed: false };
      current.steps.push(s);
    }
    return s;
  };
  for (const m of messages ?? []) {
    const content = m.content ?? [];
    if (m.role === "user") {
      const texts = content.filter((c) => c?.type !== "tool_result").map(blockText).filter(Boolean);
      const results = content.filter((c) => c?.type === "tool_result");
      if (texts.length > 0) {
        newTurn(stripUserTags(texts.join("\n")), Number(m.ts) || null);
        // A user message that mixes text and results is a follow-up: attach
        // any results it carries to the previous turn when one exists.
      }
      if (results.length > 0 && turns.length > (texts.length > 0 ? 1 : 0)) {
        const target = texts.length > 0 ? turns[turns.length - 2] : current;
        attachResults(target, results);
      } else if (results.length > 0 && current) {
        attachResults(current, results);
      }
      continue;
    }
    if (m.role !== "assistant") continue;
    const step = curStep();
    if (step.start == null) step.start = Number(m.ts) || null;
    step.end = Number(m.ts) || step.end;
    const met = m.metrics ?? null;
    if (met && (met.inputTokens != null || met.outputTokens != null)) {
      step.tokens = {
        input: (step.tokens?.input ?? 0) + (met.inputTokens ?? 0),
        output: (step.tokens?.output ?? 0) + (met.outputTokens ?? 0),
      };
    }
    for (const c of content) {
      if (c?.type === "thinking" && c.thinking) step.thinking.push(c.thinking);
      else if (c?.type === "text" && c.text) step.response.push(c.text);
      else if (c?.type === "tool_use") {
        step.toolCalls.push({ tool: c.name ?? "unknown", args: c.input ?? {}, result: "", id: c.id ?? null });
        step.closed = true; // a tool call ends the display step; text after belongs to the next step
      }
    }
  }
  // Drop the synthetic empty turn when the transcript holds no user text.
  return turns.filter((t) => t.userText || t.steps.length > 0);
}

function attachResults(turn, results) {
  if (!turn) return;
  for (const r of results) {
    const text = resultText(r);
    const open = [...turn.steps].reverse().flatMap((s) => s.toolCalls).reverse()
      .find((tc) => !tc.result && (r.tool_use_id == null || tc.id === r.tool_use_id || tc.id == null));
    const pending = [...turn.steps].reverse().flatMap((s) => s.toolCalls).reverse().find((tc) => !tc.result);
    const tc = open ?? pending;
    if (tc) {
      tc.result = text;
      delete tc.id;
    } else {
      let s = turn.steps[turn.steps.length - 1];
      if (!s) { s = { thinking: [], response: [], toolCalls: [], start: null, end: null, tokens: null, closed: false }; turn.steps.push(s); }
      s.toolCalls.push({ tool: r.name ?? "unknown", args: {}, result: text });
    }
  }
}

function resultText(r) {
  const c = r.content;
  if (typeof c === "string") return c;
  if (Array.isArray(c)) {
    return c.map((e) => {
      if (typeof e === "string") return e;
      if (e && typeof e === "object") return e.result ?? e.query ?? e.text ?? JSON.stringify(e);
      return String(e ?? "");
    }).join("\n");
  }
  if (c && typeof c === "object") return c.result ?? c.text ?? JSON.stringify(c);
  return "";
}

// Convert parsed transcript turns into the logger's turn-doc shape
// (same fields as Turn.toFields: user{ text, time? }, assistant[]).
export function transcriptTurnDocs(parsed) {
  return parsed.map((t) => {
    const user = { text: t.userText };
    if (t.userTime) user.time = formatLocal(new Date(t.userTime).toISOString());
    const doc = { user };
    const steps = t.steps.filter((s) => s.thinking.length > 0 || s.response.length > 0 || s.toolCalls.length > 0);
    if (steps.length > 0) {
      doc.assistant = steps.map((s) => {
        const a = {};
        if (s.thinking.length > 0) {
          const text = s.thinking.filter(Boolean).join("\n");
          if (text) a.thinking = text;
        }
        if (s.toolCalls.length > 0) {
          a.tool_calls = s.toolCalls.map((tc) => ({ tool: tc.tool, args: tc.args, result: tc.result ?? "" }));
        }
        if (s.start) a.time = formatLocal(new Date(s.start).toISOString());
        if (s.response.length > 0) a.response = s.response.join("");
        if (s.tokens) a.tokens = s.tokens;
        return a;
      });
    }
    return doc;
  });
}

// Rewrite the canonical transcript view atomically (tmp + rename).
export function writeTranscriptYaml(dir, docs) {
  const tmp = join(dir, ".transcript.yaml.tmp");
  const final = join(dir, "transcript.yaml");
  try {
    mkdirSync(dir, { recursive: true });
    const body = docs.map((d) => `---\n${dump(d)}`).join("");
    writeFileSync(tmp, body);
    try {
      renameSync(tmp, final);
    } catch {
      writeFileSync(final, body);
      try { unlinkSync(tmp); } catch { /* ignore */ }
    }
    return true;
  } catch { return false; }
}
