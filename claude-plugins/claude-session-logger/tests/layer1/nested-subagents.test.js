// CC-SUB nested subagents: agent_id routes tool calls into the bracketed
// subagent turn; SubagentStop attaches the final text + agent transcript.
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { drive, persistedState, readJSONL, turnFiles, useTempWorkspace, writeTranscript, yamlDocs } from "../helpers/claude-harness.js";
import { assistantEnvelope, postTool, preTool, sessionStart, stop, subagentStart, subagentStop, userEnvelope, userPrompt } from "../helpers/claude-fixtures.js";

describe("CC-SUB nested subagents", () => {
  it("CC-SUB-001 agent_id routes tool calls into the subagent turn", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-sub-001";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session, "Research this"),
      subagentStart(session, "agent-1", "Explore"),
      preTool(session, "Glob", { pattern: "*.ts" }, "toolu_10", { agent_id: "agent-1", agent_type: "Explore" }),
      postTool(session, "Glob", { pattern: "*.ts" }, "a.ts", "toolu_10", { agent_id: "agent-1", agent_type: "Explore" }),
      subagentStop(session, "agent-1", "Explore"),
    ]);
    const completed = turnFiles(dir, session);
    assert.equal(completed.length, 1);
    const doc = yamlDocs(dir, session, completed[0])[0];
    assert.deepEqual(doc.subagent, { id: "agent-1", type: "Explore" });
    assert.equal(doc.assistant[0].tool_calls[0].tool, "Glob");
    assert.equal(persistedState(dir, session).activeSubagent, null);
  });

  it("CC-SUB-002 SubagentStop attaches the final text", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-sub-002";
    await drive(dir, [
      sessionStart(session),
      subagentStart(session, "agent-2", "Plan"),
      subagentStop(session, "agent-2", "Plan"),
    ]);
    const completed = turnFiles(dir, session);
    assert.equal(completed.length, 1);
    const doc = yamlDocs(dir, session, completed[0])[0];
    assert.equal(doc.assistant[0].response, "Done, all green.");
  });

  it("CC-SUB-003 agent transcript enriches the nested doc", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-sub-003";
    const agentTp = writeTranscript(dir, "agent.jsonl", [
      userEnvelope("Find it", { sessionId: "agent-9" }),
      assistantEnvelope("Found it.", { sessionId: "agent-9", usage: { input_tokens: 10, output_tokens: 5 } }),
    ]);
    await drive(dir, [
      sessionStart(session),
      subagentStart(session, "agent-9", "Explore"),
      subagentStop(session, "agent-9", "Explore", { agent_transcript_path: agentTp, last_assistant_message: "" }),
      stop(session, { last_assistant_message: "" }),
    ]);
    const completed = turnFiles(dir, session);
    assert.equal(completed.length, 1);
    const doc = yamlDocs(dir, session, completed[0])[0];
    assert.deepEqual(doc.usage, { inputTokens: 10, outputTokens: 5 });
    assert.ok(doc.variables.find((v) => v.kind === "transcript" && v.uri === agentTp));
    const stopped = readJSONL(dir, session).find((e) => e.type === "subagent.stop");
    assert.ok(stopped);
    assert.equal(stopped.agentTranscriptPath, agentTp);
  });
});
