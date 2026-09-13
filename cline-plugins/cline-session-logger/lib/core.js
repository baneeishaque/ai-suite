// Cline logger core — Option A port of opencode-logger.ts Turn/Step model.
// Sparse mode: thinking/response stay empty (Cline hooks carry no assistant
// reasoning or text streams). Tool calls are the primary content.
// Runtime: node (mise). No bun APIs. No @cline/* imports.

export function ts() {
  return new Date().toISOString();
}

export function formatDuration(ms) {
  if (ms < 1000) return `${ms.toFixed(2)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function formatLocal(iso) {
  const d = new Date(iso);
  const date = `${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear()}`;
  let h = d.getHours();
  const ampm = h >= 12 ? "PM" : "AM";
  h = h % 12 || 12;
  const mm = String(d.getMinutes()).padStart(2, "0");
  const ss = String(d.getSeconds()).padStart(2, "0");
  const ms = String(d.getMilliseconds()).padStart(3, "0");
  const tzMatch = d.toString().match(/\(([^)]+)\)/);
  const tzAbbr = tzMatch
    ? tzMatch[1].split(" ").map((w) => w[0]).join("")
    : "LOCAL";
  const tzOffset = -d.getTimezoneOffset() / 60;
  const tzSign = tzOffset >= 0 ? "+" : "-";
  return `${date}, ${h}:${mm}:${ss}.${ms} ${ampm} ${tzAbbr}${tzSign}${Math.abs(tzOffset)}`;
}

export function normalizeResult(output) {
  if (output == null || output === "") return "";
  let raw = typeof output === "string" ? output : JSON.stringify(output);
  try {
    const parsed = JSON.parse(raw);
    if (typeof parsed === "object") return JSON.stringify(parsed, null, 2);
  } catch { /* keep raw */ }
  return raw;
}

export function modelFromHook(model) {
  if (!model) return null;
  // Cline hook payload: model { provider, slug }
  if (model.slug) return { id: model.slug, provider: model.provider ?? "" };
  if (model.id) return { id: model.id, provider: model.provider ?? "" };
  return null;
}

export class Step {
  constructor() {
    this.model = null;
    this.agent = null;
    this.thinking = [];
    this.thinkingStartTime = null;
    this.thinkingDuration = null;
    this.responseText = [];
    this.toolCalls = [];
    this.startTime = ts();
    this.endTime = null;
    this.pendingTool = null;
    this.pendingArgs = null;
  }

  get hasContent() {
    return this.thinking.length > 0 || this.toolCalls.length > 0 || this.responseText.length > 0;
  }

  toFields() {
    const a = {};
    if (this.agent) a.agent = this.agent;
    if (this.model) a.model = { id: this.model.id, provider: this.model.provider };
    if (this.thinking.length > 0) {
      const text = this.thinking.filter(Boolean).join("\n");
      if (text) a.thinking = text;
    }
    if (this.thinkingDuration != null) {
      a.thinking_duration = formatDuration(this.thinkingDuration);
      a.thinking_duration_ms = this.thinkingDuration;
    }
    if (this.toolCalls.length > 0) {
      a.tool_calls = this.toolCalls.map((tc) => ({
        tool: tc.tool,
        args: tc.args,
        result: tc.result,
      }));
    }
    if (this.startTime) a.time = formatLocal(this.startTime);
    if (this.responseText.length > 0) a.response = this.responseText.join("");
    if (this.startTime && this.endTime) {
      const ms = new Date(this.endTime).getTime() - new Date(this.startTime).getTime();
      a.duration = formatDuration(ms);
      a.duration_ms = ms;
    }
    return a;
  }
}

export class Turn {
  constructor() {
    this.userText = "";
    this.userTime = null;
    this.startTime = ts();
    this.endTime = null;
    this.steps = [];
    this.currentStep = null;
  }

  ensureStep(model) {
    if (!this.currentStep) {
      const s = new Step();
      s.model = model ?? null;
      this.steps.push(s);
      this.currentStep = s;
    }
    return this.currentStep;
  }

  toFields() {
    const userField = { text: this.userText };
    if (this.userTime) userField.time = formatLocal(this.userTime);
    const out = { user: userField };
    const stepFields = this.steps.filter((s) => s.hasContent).map((s) => s.toFields());
    if (stepFields.length > 0) out.assistant = stepFields;
    return out;
  }
}

// Finalize the active turn: close open step, stamp endTime, push to turns.
// Returns true when a turn doc was produced (mirrors opencode finalizeTurn:
// user-only turns with no assistant steps produce nothing).
export function finalizeTurn(state) {
  const t = state.turn;
  if (!t) return false;
  if (t.currentStep) t.currentStep.endTime = ts();
  t.endTime = ts();
  if (t.steps.length === 0) {
    state.turn = null;
    return false;
  }
  state.turns.push(t.toFields());
  state.turn = null;
  return true;
}

export function newSessionState() {
  return {
    turn: null, // live Turn instance (not serialized)
    turns: [], // completed turn docs
    model: null,
    title: null,
    compactedAt: null,
    created: null,
    updated: null,
    writtenTurns: 0,
    pendingFile: null, // filename of OUR pending YAML (orphans from crashes are never touched)
    clineSession: null, // { sessionId, sessionPath } link to Cline's own session store
    transcriptTurns: null, // turn count of the last transcript sync (for change logging)
    usage: null, // aggregate token/cost usage from Cline session metadata
    gitBranch: null,
    clineVersion: null, // Cline extension version from hook payloads (provenance)
  };
}

// Rebuild a live Turn instance from its plain-JSON form (see
// serializeLiveTurn in io.js). Returns null when plain is null.
export function reviveLiveTurn(plain) {
  if (!plain) return null;
  const t = new Turn();
  t.userText = plain.userText ?? "";
  t.userTime = plain.userTime ?? null;
  t.startTime = plain.startTime ?? ts();
  for (const ps of plain.steps ?? []) {
    const s = new Step();
    s.model = ps.model ?? null;
    s.agent = ps.agent ?? null;
    s.thinking = ps.thinking ?? [];
    s.thinkingStartTime = ps.thinkingStartTime ?? null;
    s.thinkingDuration = ps.thinkingDuration ?? null;
    s.responseText = ps.responseText ?? [];
    s.toolCalls = ps.toolCalls ?? [];
    s.startTime = ps.startTime ?? ts();
    s.endTime = ps.endTime ?? null;
    s.pendingTool = ps.pendingTool ?? null;
    s.pendingArgs = ps.pendingArgs ?? null;
    t.steps.push(s);
  }
  t.currentStep = t.steps.length > 0 ? t.steps[t.steps.length - 1] : null;
  return t;
}

// Build the multi-doc YAML: header + one doc per turn (same shape as
// opencode buildYAML so opencode-session-*-extractor skills keep working,
// plus origin: cline marker).
export function buildDocs(state, taskId) {
  const header = {
    session: {
      id: taskId,
      origin: "cline",
      ...(state.clineSession?.sessionId ? { cline_session_id: state.clineSession.sessionId } : {}),
      created: formatLocal(state.created ?? ts()),
      updated: formatLocal(state.updated ?? ts()),
      ...(state.compactedAt ? { compacted: formatLocal(state.compactedAt) } : {}),
    },
    model: state.model ?? { id: "unknown", provider: "unknown" },
    ...(state.title ? { title: state.title } : {}),
    ...(state.usage ? { usage: state.usage } : {}),
    ...(state.gitBranch ? { git_branch: state.gitBranch } : {}),
    ...(state.clineVersion ? { cline_version: state.clineVersion } : {}),
  };
  return [header, ...state.turns];
}
