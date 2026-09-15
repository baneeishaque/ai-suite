// CP-TR transcript hybrid: transcript_path backfills the header
// (actual model, usage rollup, agent) and the canonical transcript.yaml.
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { drive, filesIn, headerOf, readJSONL, sessionLogDir, turnFiles, useTempWorkspace, writeTranscript, writeTranscriptText, yamlDocs } from "../helpers/copilot-harness.js";
import { pingStream, sessionStart, stop, toolCallStream, transcriptRequest, userPrompt } from "../helpers/copilot-fixtures.js";

describe("CP-TR transcript hybrid", () => {
  it("CP-TR-001 transcript enriches header and writes transcript.yaml", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-tr-001";
    const tp = writeTranscript(dir, "chat.json", {
      responderUsername: "GitHub Copilot",
      requests: [transcriptRequest("Explain backends", { response: "They proxy models." })],
    });
    await drive(dir, [sessionStart(session), { ...userPrompt(session, "Explain backends"), transcript_path: tp }]);
    const header = headerOf(dir, session);
    assert.equal(header.model.id, "GPT-5.6 Luna");
    assert.equal(header.session.agent, "github.copilot.editsAgent");
    assert.deepEqual(header.usage, { promptTokens: 100, completionTokens: 50, copilotCredits: 0.8 });
    assert.ok(existsSync(join(sessionLogDir(dir, session), "transcript.yaml")));
    const synced = readJSONL(dir, session).find((e) => e.type === "transcript.sync");
    assert.ok(synced);
    assert.equal(synced.turns, 1);
  });

  it("CP-TR-002 usage, variables, and errors land in transcript docs", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-tr-002";
    const req = transcriptRequest("Fix it", {
      response: "Patched the backend.",
      promptTokens: 1000,
      completionTokens: 200,
      copilotCredits: 2.5,
      variableData: { variables: [{ kind: "file", uri: "file:///src/a.ts", value: "x".repeat(600) }] },
    });
    req.result = { details: "failed", metadata: { agentId: "github.copilot.editsAgent", codeBlocks: [{}, {}] }, errorDetails: { code: "quota_exceeded" } };
    const tp = writeTranscript(dir, "chat.json", { requests: [req] });
    await drive(dir, [sessionStart(session), { ...userPrompt(session, "Fix it"), transcript_path: tp }]);
    const docs = yamlDocs(dir, session, "transcript.yaml");
    assert.equal(docs[0].usage.promptTokens, 1000);
    assert.equal(docs[0].variables[0].uri, "file:///src/a.ts");
    assert.equal(docs[0].variables[0].snippet.length, 500);
    assert.equal(docs[0].code_blocks, 2);
    assert.equal(docs[0].error, "quota_exceeded");
    assert.equal(docs[0].assistant[0].response, "Patched the backend.");
  });

  it("CP-TR-003 garbage transcript is ignored without crashing", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-tr-003";
    const tp = writeTranscript(dir, "chat.json", "not json{{{");
    await drive(dir, [sessionStart(session), { ...userPrompt(session, "Hi"), transcript_path: tp }]);
    const header = headerOf(dir, session);
    assert.equal(header.model.id, "unknown");
    assert.ok(!("usage" in header));
    assert.ok(!filesIn(dir, session).includes("transcript.yaml"));
  });

  it("CP-TR-004 missing transcript_path is a no-op", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-tr-004";
    await drive(dir, [sessionStart(session), userPrompt(session, "Hi")]);
    assert.ok(!filesIn(dir, session).includes("transcript.yaml"));
  });

  it("CP-TR-005 live stream records versions and turn docs", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-tr-005";
    const tp = writeTranscriptText(dir, "live.jsonl", pingStream(session));
    await drive(dir, [sessionStart(session), { ...userPrompt(session, "Ping Test"), transcript_path: tp }]);
    const header = headerOf(dir, session);
    assert.equal(header.session.producer, "copilot-agent");
    assert.equal(header.session.copilot_version, "0.66.2026091401");
    assert.equal(header.session.vscode_version, "1.138.0-insider");
    const docs = yamlDocs(dir, session, "transcript.yaml");
    assert.equal(docs[0].user.text, "Ping Test");
    assert.equal(docs[0].user.message_id, "evt-2");
    assert.equal(docs[0].assistant[0].response, "Pong.");
    assert.equal(docs[0].assistant[0].message_id, "msg-1");
    assert.deepEqual(docs[0].turn_ids, ["0"]);
  });

  it("CP-TR-006 Stop backfills a tool-less turn from the stream", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-tr-006";
    const tp = writeTranscriptText(dir, "live.jsonl", pingStream(session));
    await drive(dir, [
      sessionStart(session),
      { ...userPrompt(session, "Ping Test"), transcript_path: tp },
      { ...stop(session), transcript_path: tp },
    ]);
    const completed = turnFiles(dir, session);
    assert.equal(completed.length, 1);
    const doc = yamlDocs(dir, session, completed[0])[0];
    assert.equal(doc.user.text, "Ping Test");
    assert.equal(doc.assistant[0].response, "Pong.");
  });

  it("CP-TR-007 stream toolRequests args parse from JSON strings", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-tr-007";
    const tp = writeTranscriptText(dir, "live.jsonl", toolCallStream(session));
    await drive(dir, [sessionStart(session), { ...userPrompt(session, "List files"), transcript_path: tp }]);
    const docs = yamlDocs(dir, session, "transcript.yaml");
    assert.equal(docs[0].assistant[0].reasoning, "Need the file list first.");
    assert.deepEqual(docs[0].assistant[0].tool_requests, [
      { tool: "copilot_listDirectory", args: { path: "src" }, toolUseId: "toolu_1" },
    ]);
  });
});
