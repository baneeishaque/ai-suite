// Claude transcript hybrid: best-effort parse of the transcript_path file
// (~/.claude/projects/<slug>/<session>.jsonl, one envelope per line) into
// canonical turn docs plus header enrichment.
//
// Envelope shapes observed live:
// - {type:"user", message:{role:"user",content}, uuid, parentUuid,
//   timestamp, isSidechain, isMeta, cwd, sessionId, version, gitBranch}
// - {type:"assistant", message:{role:"assistant",content}, uuid,
//   parentUuid, model, usage{...}, ...} where content is a string or an
//   array of blocks ({type:"text",text} | {type:"thinking",thinking} |
//   {type:"tool_use",id,name,input} | {type:"tool_result",...})
// - {type:"summary", summary, ...} on compaction; {type:"mode"|
//   "permission-mode"|"file-history-snapshot", ...} bookkeeping.
// Sidechain entries (subagent internals) are skipped: subagent activity is
// captured via SubagentStart/Stop plus agent transcripts instead.
// Any failure returns null — the hook-driven log stays primary.
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { dump } from "js-yaml";

const MAX_DOCS = 500; // bound transcript.yaml growth on very long sessions

function asIso(value) {
  if (typeof value !== "string" && typeof value !== "number") return null;
  const ms = typeof value === "number" ? value : Date.parse(value);
  return Number.isFinite(ms) ? new Date(ms).toISOString() : null;
}

function textContent(content) {
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  return content
    .filter((b) => b && typeof b === "object" && b.type === "text" && typeof b.text === "string")
    .map((b) => b.text)
    .join("");
}

function thinkingContent(content) {
  if (!Array.isArray(content)) return "";
  return content
    .filter((b) => b && typeof b === "object" && b.type === "thinking" && typeof b.thinking === "string")
    .map((b) => b.thinking)
    .join("\n");
}

function toolUseBlocks(content) {
  if (!Array.isArray(content)) return [];
  return content.filter((b) => b && typeof b === "object" && b.type === "tool_use");
}

function normalizeUsage(usage) {
  if (!usage || typeof usage !== "object") return null;
  const out = {};
  if (Number.isFinite(usage.input_tokens)) out.inputTokens = usage.input_tokens;
  if (Number.isFinite(usage.output_tokens)) out.outputTokens = usage.output_tokens;
  if (Number.isFinite(usage.cache_read_input_tokens)) out.cacheReadTokens = usage.cache_read_input_tokens;
  if (Number.isFinite(usage.cache_creation_input_tokens)) out.cacheCreationTokens = usage.cache_creation_input_tokens;
  return Object.keys(out).length > 0 ? out : null;
}

function assistantStep(envelope) {
  const message = envelope?.message ?? {};
  const step = {};
  const text = textContent(message.content);
  if (text !== "") step.response = text;
  const thinking = thinkingContent(message.content);
  if (thinking !== "") step.thinking = thinking;
  const uses = toolUseBlocks(message.content);
  if (uses.length > 0) {
    step.tool_requests = uses.map((b) => ({
      tool: b.name ?? "unknown",
      args: b.input && typeof b.input === "object" ? b.input : {},
      ...(b.id ? { toolUseId: b.id } : {}),
    }));
  }
  if (typeof envelope?.model === "string" && envelope.model !== "") {
    step.model = { id: envelope.model, provider: "claude" };
  }
  const usage = normalizeUsage(envelope?.usage);
  if (usage) step.usage = usage;
  return step;
}

function userDoc(envelope, assistantEnvelopes) {
  const message = envelope?.message ?? {};
  const text = textContent(message.content) || (typeof message.content === "string" ? message.content : "");
  const doc = { user: { text } };
  const userTime = asIso(envelope?.timestamp);
  if (userTime) doc.user.time = userTime;
  if (typeof envelope?.uuid === "string") doc.user.uuid = envelope.uuid;
  if (envelope?.isMeta) doc.user.is_meta = true;
  const steps = [];
  for (const ev of assistantEnvelopes) {
    const step = assistantStep(ev);
    if (Object.keys(step).length > 0) steps.push(step);
  }
  if (steps.length > 0) doc.assistant = steps;
  if (typeof envelope?.parentUuid === "string") doc.parent_uuid = envelope.parentUuid;
  return doc;
}

// Parse a transcript file into { model, agent, mode, title, usage,
// gitBranch, claudeVersion, docs, lastPair }. Returns null when the file
// is missing, unparsable, or holds no turns.
export function parseTranscriptFile(transcriptPath) {
  try {
    const raw = readFileSync(transcriptPath, "utf-8");
    if (!raw || !raw.trim()) return null;
    const envelopes = [];
    for (const line of raw.split("\n")) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      try {
        const envelope = JSON.parse(trimmed);
        if (envelope && typeof envelope === "object") envelopes.push(envelope);
      } catch { /* skip corrupt lines */ }
    }
    if (envelopes.length === 0) return null;
    const docs = [];
    let currentUser = null;
    let currentAssistant = [];
    const flush = () => {
      if (!currentUser) return;
      const doc = userDoc(currentUser, currentAssistant);
      if (doc.user?.text || doc.assistant) docs.push(doc);
      currentUser = null;
      currentAssistant = [];
    };
    for (const ev of envelopes) {
      if (ev.isSidechain) continue;
      if (ev.type === "user") {
        flush();
        currentUser = ev;
        currentAssistant = [];
      } else if (ev.type === "assistant") {
        if (!currentUser) continue;
        currentAssistant.push(ev);
      } else if (ev.type === "summary") {
        flush();
        if (typeof ev.summary === "string" && ev.summary !== "") {
          docs.push({ summary: ev.summary.slice(0, 2000) });
        }
      }
    }
    flush();
    const kept = docs.slice(-MAX_DOCS);
    if (kept.length === 0) return null;
    let model = null;
    let gitBranch = null;
    let claudeVersion = null;
    const usage = { inputTokens: 0, outputTokens: 0 };
    let hasUsage = false;
    for (const ev of envelopes) {
      if (ev.isSidechain) continue;
      if (ev.type === "assistant" && typeof ev.model === "string" && ev.model !== "") model = ev.model;
      if (typeof ev.gitBranch === "string" && ev.gitBranch !== "") gitBranch = ev.gitBranch;
      if ((ev.type === "user" || ev.type === "assistant") && ev.version != null) claudeVersion = String(ev.version);
      const u = normalizeUsage(ev.usage);
      if (u) {
        hasUsage = true;
        usage.inputTokens += u.inputTokens ?? 0;
        usage.outputTokens += u.outputTokens ?? 0;
        if (u.cacheReadTokens != null) usage.cacheReadTokens = (usage.cacheReadTokens ?? 0) + u.cacheReadTokens;
        if (u.cacheCreationTokens != null) usage.cacheCreationTokens = (usage.cacheCreationTokens ?? 0) + u.cacheCreationTokens;
      }
    }
    // Meta traffic (local-command caveats, slash-command expansions) never
    // becomes the session title.
    const firstUser = kept.find((d) => d.user?.text && !d.user?.is_meta)?.user?.text ?? null;
    let lastPair = null;
    for (let i = kept.length - 1; i >= 0; i--) {
      const responses = (kept[i].assistant ?? []).map((s) => s.response).filter((r) => typeof r === "string" && r !== "");
      if (kept[i].user?.text && responses.length > 0) {
        lastPair = { userText: kept[i].user.text, assistantText: responses.join("\n") };
        break;
      }
    }
    return {
      model,
      agent: null, // agent identity arrives via hook payloads, not envelopes
      mode: null,
      title: firstUser ? firstUser.slice(0, 120) : null,
      usage: hasUsage ? usage : null,
      gitBranch,
      claudeVersion,
      docs: kept,
      lastPair,
    };
  } catch { return null; }
}

export function writeTranscriptYaml(dir, docs) {
  const body = docs.map((d) => `---\n${dump(d)}`).join("");
  writeFileSync(join(dir, "transcript.yaml"), body);
}
