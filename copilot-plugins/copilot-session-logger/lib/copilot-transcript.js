// Copilot transcript hybrid: best-effort parse of the transcript_path file
// into canonical turn docs plus header enrichment.
//
// Two shapes are supported (both observed live):
// A. Live transcript JSONL event stream (*.jsonl under
//    .../GitHub.copilot-chat/transcripts/<session>.jsonl), one envelope
//    per line: {type, data, id, timestamp, parentId}. Event types seen:
//    session.start {sessionId, version, producer, copilotVersion,
//      vscodeVersion, startTime}, user.message {content, attachments},
//    assistant.turn_start {turnId}, assistant.message {messageId, content,
//      toolRequests [{toolCallId, name, arguments}], reasoningText},
//    tool.execution_start {toolCallId, toolName, arguments},
//    tool.execution_complete {toolCallId, success}, assistant.turn_end.
//    NOTE: the stream carries NO model/token/credit fields.
// B. Manual chat export (whole-file JSON {requests: [...]}): per-request
//    modelId, result{details,metadata,timings,errorDetails}, token and
//    credit counters, variableData. Only source for usage data.
//
// Returns { provenance, model, agent, mode, title, usage, docs, lastPair }
// or null. Any failure returns null — the hook-driven log stays primary.
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { dump } from "js-yaml";

const MAX_DOCS = 500; // bound transcript.yaml growth on very long sessions
const MAX_SNIPPET = 500; // variable snippet cap (URIs + snippets policy)

function asIso(value) {
  if (typeof value !== "string" && typeof value !== "number") return null;
  const ms = typeof value === "number" ? value : Date.parse(value);
  return Number.isFinite(ms) ? new Date(ms).toISOString() : null;
}

function parseArgs(value) {
  if (value == null) return {};
  if (typeof value === "object") return value;
  if (typeof value !== "string" || value === "") return {};
  try {
    const parsed = JSON.parse(value);
    return parsed && typeof parsed === "object" ? parsed : { _raw: value.slice(0, 2000) };
  } catch { return { _raw: value.slice(0, 2000) }; }
}

// ---- shape A: live JSONL event stream ----

function streamDoc(userEvent, assistantEvents) {
  const content = userEvent?.data?.content;
  const doc = { user: { text: typeof content === "string" ? content : "" } };
  const userTime = asIso(userEvent?.timestamp);
  if (userTime) doc.user.time = userTime;
  if (userEvent?.id) doc.user.message_id = userEvent.id;
  const attachments = userEvent?.data?.attachments;
  if (Array.isArray(attachments) && attachments.length > 0) doc.user.attachments = attachments.length;
  const steps = [];
  for (const ev of assistantEvents) {
    if (ev.type !== "assistant.message") continue;
    const data = ev.data ?? {};
    const step = {};
    if (typeof data.content === "string" && data.content !== "") step.response = data.content;
    if (typeof data.messageId === "string") step.message_id = data.messageId;
    if (typeof data.reasoningText === "string" && data.reasoningText !== "") step.reasoning = data.reasoningText;
    const requests = Array.isArray(data.toolRequests) ? data.toolRequests : [];
    if (requests.length > 0) {
      step.tool_requests = requests.map((r) => ({
        tool: r?.name ?? "unknown",
        args: parseArgs(r?.arguments),
        ...(r?.toolCallId ? { toolUseId: r.toolCallId } : {}),
      }));
    }
    if (Object.keys(step).length > 0) steps.push(step);
  }
  if (steps.length > 0) doc.assistant = steps;
  const turnIds = [...new Set(assistantEvents.filter((ev) => ev.data?.turnId != null).map((ev) => String(ev.data.turnId)))];
  if (turnIds.length > 0) doc.turn_ids = turnIds;
  return doc;
}

function parseStream(raw) {
  const events = [];
  for (const line of raw.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try {
      const envelope = JSON.parse(trimmed);
      if (envelope && typeof envelope === "object" && typeof envelope.type === "string") events.push(envelope);
    } catch { /* skip corrupt lines */ }
  }
  if (events.length === 0) return null;
  if (!events.some((e) => e.type === "session.start" || e.type === "user.message" || e.type === "assistant.message")) {
    return null;
  }
  const provenance = {};
  const docs = [];
  let currentUser = null;
  let currentAssistant = [];
  const flush = () => {
    if (!currentUser) return;
    const doc = streamDoc(currentUser, currentAssistant);
    if (doc.user?.text || doc.assistant) docs.push(doc);
    currentUser = null;
    currentAssistant = [];
  };
  for (const ev of events) {
    if (ev.type === "session.start") {
      const d = ev.data ?? {};
      if (typeof d.producer === "string") provenance.producer = d.producer;
      if (typeof d.copilotVersion === "string") provenance.copilotVersion = d.copilotVersion;
      if (typeof d.vscodeVersion === "string") provenance.vscodeVersion = d.vscodeVersion;
    } else if (ev.type === "user.message") {
      flush();
      currentUser = ev;
      currentAssistant = [];
    } else if (ev.type === "assistant.turn_start" || ev.type === "assistant.message" || ev.type === "assistant.turn_end") {
      if (!currentUser) continue; // assistant content without a user turn: ignore
      currentAssistant.push(ev);
    }
    // tool.execution_* events duplicate assistant.message.toolRequests:
    // skipped (kept in reserve for arg backfill if toolRequests ever empties).
  }
  flush();
  const kept = docs.slice(-MAX_DOCS);
  if (kept.length === 0) return null;
  const firstUser = kept.find((d) => d.user?.text)?.user?.text ?? null;
  let lastPair = null;
  for (let i = kept.length - 1; i >= 0; i--) {
    const responses = (kept[i].assistant ?? []).map((s) => s.response).filter((r) => typeof r === "string" && r !== "");
    if (kept[i].user?.text && responses.length > 0) {
      lastPair = { userText: kept[i].user.text, assistantText: responses.join("\n") };
      break;
    }
  }
  return {
    provenance: Object.keys(provenance).length > 0 ? provenance : null,
    model: null, // the stream carries no model identity
    agent: null,
    mode: null,
    title: firstUser ? firstUser.slice(0, 120) : null,
    usage: null, // the stream carries no token/credit counters
    docs: kept,
    lastPair,
  };
}

// ---- shape B: manual chat export {requests: [...]} ----

function textOf(parts) {
  if (!Array.isArray(parts)) return "";
  return parts
    .filter((p) => p && typeof p === "object" && typeof p.value === "string" && !p.toolCallId)
    .map((p) => p.value)
    .join("");
}

function snippetOf(value) {
  if (typeof value !== "string" || value === "") return null;
  return value.length > MAX_SNIPPET ? value.slice(0, MAX_SNIPPET) : value;
}

function variablesOf(variableData) {
  const vars = variableData?.variables;
  if (!Array.isArray(vars)) return null;
  const out = [];
  for (const v of vars) {
    if (!v || typeof v !== "object") continue;
    out.push({
      kind: v.kind ?? v.id ?? "unknown",
      ...((v.uri ?? v.location ?? v.name) ? { uri: String(v.uri ?? v.location ?? v.name) } : {}),
      ...(snippetOf(v.value ?? v.content) ? { snippet: snippetOf(v.value ?? v.content) } : {}),
    });
  }
  return out.length > 0 ? out : null;
}

// Actual model name from result.details ("GPT-5.6 Luna • 0.8 credits").
function modelOf(request) {
  const details = request?.result?.details;
  if (typeof details === "string") {
    const name = details.split("•")[0].trim();
    if (name) return name;
  }
  const id = request?.modelId;
  return typeof id === "string" && id !== "" && id !== "copilot/auto" ? id : null;
}

function requestDoc(request) {
  const message = request?.message ?? {};
  const userText = typeof message.text === "string" ? message.text : "";
  const userTime = asIso(request?.timestamp);
  const response = Array.isArray(request?.response) ? request.response : [];
  const doc = { user: { text: userText, ...(userTime ? { time: userTime } : {}) } };
  if (request?.requestId) doc.request_id = String(request.requestId);
  if (request?.responseId) doc.response_id = String(request.responseId);
  const assistant = [];
  const text = textOf(response);
  if (text !== "") {
    const step = { response: text };
    const model = modelOf(request);
    if (model) step.model = { id: model, provider: "copilot" };
    assistant.push(step);
  }
  const toolCalls = response.filter((p) => p && typeof p === "object" && p.toolCallId);
  if (toolCalls.length > 0) {
    assistant.push({
      tool_calls: toolCalls.map((p) => ({
        tool: p.toolId ?? "unknown",
        args: {},
        result: p.pastTenseMessage ?? p.invocationMessage ?? "",
        toolUseId: p.toolCallId,
      })),
    });
  }
  if (assistant.length > 0) doc.assistant = assistant;
  const usage = {
    ...(Number.isFinite(request?.promptTokens) ? { promptTokens: request.promptTokens } : {}),
    ...(Number.isFinite(request?.completionTokens) ? { completionTokens: request.completionTokens } : {}),
    ...(Number.isFinite(request?.copilotCredits) ? { copilotCredits: request.copilotCredits } : {}),
  };
  if (Object.keys(usage).length > 0) doc.usage = usage;
  const timings = {
    ...(Number.isFinite(request?.elapsedMs) ? { elapsedMs: request.elapsedMs } : {}),
    ...(Number.isFinite(request?.timeSpentWaiting) ? { timeSpentWaitingMs: request.timeSpentWaiting } : {}),
  };
  if (Object.keys(timings).length > 0) doc.timings = timings;
  const variables = variablesOf(request?.variableData);
  if (variables) doc.variables = variables;
  const codeBlocks = request?.result?.metadata?.codeBlocks;
  if (Array.isArray(codeBlocks)) doc.code_blocks = codeBlocks.length;
  const details = request?.result?.details;
  if (typeof details === "string" && details !== "") doc.result = details.slice(0, 500);
  const errorCode = request?.result?.errorDetails?.code;
  if (typeof errorCode === "string" && errorCode !== "") doc.error = errorCode;
  return doc;
}

function parseExport(data) {
  const requests = Array.isArray(data) ? data : data?.requests ?? null;
  if (!Array.isArray(requests) || requests.length === 0) return null;
  const kept = requests.slice(-MAX_DOCS);
  const docs = kept.map(requestDoc).filter((d) => d.user?.text || d.assistant);
  if (docs.length === 0) return null;
  const first = kept[0];
  const agent = typeof first?.agent === "string" ? first.agent : first?.agent?.id ?? null;
  const modeInfo = first?.modeInfo ?? null;
  const usage = { promptTokens: 0, completionTokens: 0, copilotCredits: 0 };
  let hasUsage = false;
  for (const r of kept) {
    if (Number.isFinite(r?.promptTokens)) { usage.promptTokens += r.promptTokens; hasUsage = true; }
    if (Number.isFinite(r?.completionTokens)) { usage.completionTokens += r.completionTokens; hasUsage = true; }
    if (Number.isFinite(r?.copilotCredits)) { usage.copilotCredits += r.copilotCredits; hasUsage = true; }
  }
  // Last actual model wins (mid-session model switches land here).
  let model = null;
  for (const r of kept) model = modelOf(r) ?? model;
  const title = typeof first?.message?.text === "string" ? first.message.text.slice(0, 120) || null : null;
  let lastPair = null;
  for (let i = docs.length - 1; i >= 0; i--) {
    const responses = (docs[i].assistant ?? []).map((s) => s.response).filter((r) => typeof r === "string" && r !== "");
    if (docs[i].user?.text && responses.length > 0) {
      lastPair = { userText: docs[i].user.text, assistantText: responses.join("\n") };
      break;
    }
  }
  return {
    provenance: null,
    model,
    agent: typeof agent === "string" && agent !== "" ? agent : null,
    mode: modeInfo && typeof modeInfo === "object"
      ? { kind: modeInfo.kind ?? null, permissionLevel: modeInfo.permissionLevel ?? null }
      : null,
    title,
    usage: hasUsage ? usage : null,
    docs,
    lastPair,
  };
}

// Parse a transcript file into { provenance, model, agent, mode, title,
// usage, docs, lastPair }. Returns null when the file is missing,
// unparsable, or holds no turns.
export function parseTranscriptFile(transcriptPath) {
  try {
    const raw = readFileSync(transcriptPath, "utf-8");
    if (!raw || !raw.trim()) return null;
    // Shape B first: whole-file JSON with a requests array.
    try {
      const data = JSON.parse(raw);
      if (data && typeof data === "object") {
        const exported = parseExport(data);
        if (exported) return exported;
      }
    } catch { /* not whole-file JSON: fall through to the stream */ }
    // Shape A: JSONL event stream.
    return parseStream(raw);
  } catch { return null; }
}

export function writeTranscriptYaml(dir, docs) {
  const body = docs.map((d) => `---\n${dump(d)}`).join("");
  writeFileSync(join(dir, "transcript.yaml"), body);
}
