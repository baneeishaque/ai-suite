// Copilot transcript hybrid: best-effort parse of the transcript_path file
// handed to hooks (VS Code chat session shape: { requests: [...] }) into
// canonical turn docs plus header enrichment (actual model, usage rollup).
// The transcript format is NOT a stable hook API and drifts — every access
// is defensive and any failure returns null (the hook-driven log stays
// the primary record).
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

// Parse a transcript file into { model, agent, mode, title, usage, docs }.
// Returns null when the file is missing, unparsable, or holds no requests.
export function parseTranscriptFile(transcriptPath) {
  try {
    const raw = readFileSync(transcriptPath, "utf-8");
    const data = JSON.parse(raw);
    const requests = Array.isArray(data) ? data : data?.requests ?? data?.messages ?? null;
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
    return {
      model,
      agent: typeof agent === "string" && agent !== "" ? agent : null,
      mode: modeInfo && typeof modeInfo === "object"
        ? { kind: modeInfo.kind ?? null, permissionLevel: modeInfo.permissionLevel ?? null }
        : null,
      title,
      usage: hasUsage ? usage : null,
      docs,
    };
  } catch { return null; }
}

export function writeTranscriptYaml(dir, docs) {
  const body = docs.map((d) => `---\n${dump(d)}`).join("");
  writeFileSync(join(dir, "transcript.yaml"), body);
}
