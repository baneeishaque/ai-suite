// CC-TR transcript hybrid: ~/.claude/projects envelopes backfill the
// header (model, branch, version, usage) and canonical transcript.yaml.
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { drive, filesIn, headerOf, readJSONL, sessionLogDir, useTempWorkspace, writeTranscript, yamlDocs } from "../helpers/claude-harness.js";
import { assistantEnvelope, sessionStart, userEnvelope, userPrompt } from "../helpers/claude-fixtures.js";

describe("CC-TR transcript hybrid", () => {
  it("CC-TR-001 envelopes enrich header and write transcript.yaml", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-tr-001";
    const tp = writeTranscript(dir, "t.jsonl", [
      userEnvelope("Explain backends", { sessionId: session }),
      assistantEnvelope("They proxy models.", { sessionId: session }),
    ]);
    await drive(dir, [sessionStart(session), { ...userPrompt(session, "Explain backends"), transcript_path: tp }]);
    const header = headerOf(dir, session);
    assert.equal(header.model.id, "claude-opus-4-6");
    assert.equal(header.session.git_branch, "main");
    assert.equal(header.claude_version, "2.1.235");
    assert.deepEqual(header.usage, { inputTokens: 100, outputTokens: 50 });
    assert.ok(existsSync(join(sessionLogDir(dir, session), "transcript.yaml")));
    const synced = readJSONL(dir, session).find((e) => e.type === "transcript.sync");
    assert.ok(synced);
    assert.equal(synced.turns, 1);
  });

  it("CC-TR-002 thinking and tool_use blocks land in transcript docs", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-tr-002";
    const asst = assistantEnvelope("", { sessionId: session });
    asst.message.content = [
      { type: "thinking", thinking: "Check the schema first." },
      { type: "text", text: "Schema looks fine." },
      { type: "tool_use", id: "toolu_50", name: "Read", input: { file_path: "db.sql" } },
    ];
    const tp = writeTranscript(dir, "t.jsonl", [userEnvelope("Audit this", { sessionId: session }), asst]);
    await drive(dir, [sessionStart(session), { ...userPrompt(session, "Audit this"), transcript_path: tp }]);
    const docs = yamlDocs(dir, session, "transcript.yaml");
    assert.equal(docs[0].assistant[0].thinking, "Check the schema first.");
    assert.equal(docs[0].assistant[0].response, "Schema looks fine.");
    assert.deepEqual(docs[0].assistant[0].tool_requests, [
      { tool: "Read", args: { file_path: "db.sql" }, toolUseId: "toolu_50" },
    ]);
  });

  it("CC-TR-003 sidechain entries are skipped", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-tr-003";
    const side = userEnvelope("hidden work", { sessionId: session });
    side.isSidechain = true;
    const tp = writeTranscript(dir, "t.jsonl", [
      userEnvelope("Visible task", { sessionId: session }),
      assistantEnvelope("Visible answer.", { sessionId: session }),
      side,
    ]);
    await drive(dir, [sessionStart(session), { ...userPrompt(session, "Visible task"), transcript_path: tp }]);
    const docs = yamlDocs(dir, session, "transcript.yaml");
    assert.equal(docs.length, 1);
    assert.equal(docs[0].user.text, "Visible task");
  });

  it("CC-TR-004 garbage transcript is ignored without crashing", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-tr-004";
    const tp = writeTranscript(dir, "t.jsonl", []);
    await drive(dir, [sessionStart(session), { ...userPrompt(session, "Hi"), transcript_path: tp }]);
    const header = headerOf(dir, session);
    assert.equal(header.model.id, "claude-opus-4-6"); // hook model survives
    assert.ok(!filesIn(dir, session).includes("transcript.yaml"));
  });

  it("CC-TR-005 meta messages never become the title", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-tr-005";
    const meta = userEnvelope("<local-command-caveat>Caveat.</local-command-caveat>", { sessionId: session });
    meta.isMeta = true;
    const tp = writeTranscript(dir, "t.jsonl", [
      meta,
      userEnvelope("Real task", { sessionId: session }),
      assistantEnvelope("On it.", { sessionId: session }),
    ]);
    await drive(dir, [sessionStart(session), { ...userPrompt(session, "Real task"), transcript_path: tp }]);
    assert.equal(headerOf(dir, session).title, "Real task");
  });
});
