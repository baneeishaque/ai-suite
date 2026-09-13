// CL-SE Cline session bridge: discovery, metadata enrichment, transcript
// backfill (cf. real session 1789302214401_qzx8b: sparse hook payloads vs
// rich on-disk transcript with thinking/text/tool_use/tool_result blocks).
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { mkdirSync, writeFileSync, mkdtempSync, existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import {
  loadTranscriptDocs,
  parseConvTs,
  parseTranscript,
  resolveSession,
  stripUserTags,
  transcriptTurnDocs,
} from "../../lib/cline-session.js";
import { handle } from "../../lib/router.js";

function seedSession(sessionsRoot, sessionId, { workspace, messages, meta = {} }) {
  const dir = join(sessionsRoot, sessionId);
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, `${sessionId}.json`), JSON.stringify({
    session_id: sessionId,
    model: "deepseek/deepseek-v4-flash",
    provider: "cline-pass",
    started_at: new Date(1789302215000).toISOString(),
    workspace_root: workspace,
    prompt: "Replay with Ok",
    metadata: {
      title: "Replay with Ok",
      modelId: "deepseek/deepseek-v4-flash",
      git: { branch: "main" },
      aggregateUsage: { inputTokens: 43729, outputTokens: 1883, cacheReadTokens: 16128, cacheWriteTokens: 0, totalCost: 0 },
      ...meta,
    },
  }));
  writeFileSync(join(dir, `${sessionId}.messages.json`), JSON.stringify({
    version: 1, sessionId, messages,
  }));
  return dir;
}

const MSGS = [
  { id: "m0", role: "user", ts: 1789302215432, content: [{ type: "text", text: '<user_input mode="act">Replay with Ok</user_input>' }] },
  {
    id: "m1", role: "assistant", ts: 1789302258648, metrics: { inputTokens: 11773, outputTokens: 856 },
    content: [
      { type: "thinking", thinking: "The user said Replay with Ok - minimal context." },
      { type: "tool_use", id: "call_1", name: "run_commands", input: { commands: ["git status"] } },
    ],
  },
  {
    id: "m2", role: "user", ts: 1789302297313,
    content: [{ type: "tool_result", tool_use_id: "call_1", name: "run_commands", content: [{ result: "M foo.ts" }] }],
  },
  {
    id: "m3", role: "assistant", ts: 1789302311675, metrics: { inputTokens: 15717, outputTokens: 504 },
    content: [
      { type: "thinking", thinking: "Result shows a modified file." },
      { type: "text", text: "I see one modified file." },
      { type: "tool_use", id: "call_2", name: "ask_question", input: { question: "Proceed?" } },
    ],
  },
];

describe("CL-SE session bridge", () => {
  it("CL-SE-001 parses conv timestamp from taskId", () => {
    assert.equal(parseConvTs("conv_1789302215430_s56a4nd"), 1789302215430);
    assert.equal(parseConvTs("task-plain"), null);
  });

  it("CL-SE-002 strips user_input tags", () => {
    assert.equal(stripUserTags('<user_input mode="act">Replay with Ok</user_input>'), "Replay with Ok");
  });

  it("CL-SE-003 segments transcript into turns with thinking/text/tools", () => {
    const turns = parseTranscript(MSGS);
    assert.equal(turns.length, 1);
    assert.equal(turns[0].userText, "Replay with Ok");
    assert.equal(turns[0].steps.length, 2);
    assert.deepEqual(turns[0].steps[0].thinking, ["The user said Replay with Ok - minimal context."]);
    assert.equal(turns[0].steps[0].toolCalls[0].tool, "run_commands");
    assert.equal(turns[0].steps[0].toolCalls[0].result, "M foo.ts");
    assert.deepEqual(turns[0].steps[1].response, ["I see one modified file."]);
  });

  it("CL-SE-004 tool_result-only user message does not open a turn", () => {
    const turns = parseTranscript([MSGS[1], MSGS[2]]);
    assert.equal(turns.length, 1);
    assert.equal(turns[0].userText, "");
  });

  it("CL-SE-005 resolves session by workspace + conv timestamp", (t) => {
    const sessionsRoot = mkdtempSync(join(tmpdir(), "cline-sessions-"));
    t.after(() => {});
    const ws = mkdtempSync(join(tmpdir(), "cline-ws-"));
    const prev = process.env.CLINE_SESSIONS_ROOT;
    process.env.CLINE_SESSIONS_ROOT = sessionsRoot;
    t.after(() => { process.env.CLINE_SESSIONS_ROOT = prev; });
    seedSession(sessionsRoot, "1789302214401_qzx8b", { workspace: ws, messages: MSGS });
    seedSession(sessionsRoot, "other_session", { workspace: "/elsewhere", messages: MSGS });
    const found = resolveSession("conv_1789302215430_s56a4nd", ws, null);
    assert.ok(found);
    assert.equal(found.sessionId, "1789302214401_qzx8b");
    const miss = resolveSession("conv_1789302215430_s56a4nd", "/nope", null);
    assert.equal(miss, null);
  });

  it("CL-SE-006 hook run enriches header and writes transcript.yaml", async (t) => {
    const sessionsRoot = mkdtempSync(join(tmpdir(), "cline-sessions-"));
    const ws = mkdtempSync(join(tmpdir(), "cline-ws-"));
    const prev = process.env.CLINE_SESSIONS_ROOT;
    process.env.CLINE_SESSIONS_ROOT = sessionsRoot;
    t.after(() => { process.env.CLINE_SESSIONS_ROOT = prev; });
    seedSession(sessionsRoot, "1789302214401_qzx8b", { workspace: ws, messages: MSGS });
    const task = "conv_1789302215430_s56a4nd";
    const base = { taskId: task, timestamp: String(Date.now()), workspaceRoots: [ws], model: { provider: "x", slug: "y" } };
    await handle({ ...base, hookName: "PostToolUse", postToolUse: { tool: "run_commands", parameters: {}, result: "M foo.ts", success: true } });
    await handle({ ...base, hookName: "TaskComplete", taskComplete: {} });
    const dir = join(ws, ".cline", "run-logs", task);
    const files = readdirSync(dir);
    assert.ok(files.includes("transcript.yaml"), `files: ${files}`);
    assert.ok(files.some((f) => f.endsWith(".payloads.jsonl")), `files: ${files}`);
    const ty = readFileSync(join(dir, "transcript.yaml"), "utf-8");
    assert.ok(ty.includes("Replay with Ok"));
    assert.ok(ty.includes("run_commands"));
    assert.ok(ty.includes("minimal context"));
    const headerFile = files.find((f) => f.startsWith("000-header-"));
    const header = readFileSync(join(dir, headerFile), "utf-8");
    assert.ok(header.includes("deepseek/deepseek-v4-flash"), header.slice(0, 400));
    assert.ok(header.includes("1789302214401_qzx8b"), header.slice(0, 600));
    assert.ok(header.includes("inputTokens"), header);
    const docs = loadTranscriptDocs(join(sessionsRoot, "1789302214401_qzx8b"), "1789302214401_qzx8b");
    assert.ok(docs && docs.length === 1);
    assert.ok(transcriptTurnDocs(parseTranscript(MSGS))[0].assistant[1].tokens);
  });
});
