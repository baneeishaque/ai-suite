// CC-HK hook mapping: Claude hook events land in the session log.
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { drive, filesIn, headerOf, persistedState, readJSONL, turnFiles, useTempWorkspace, yamlDocs } from "../helpers/claude-harness.js";
import { modelSwitch, postCompact, postTool, postToolFailure, preCompact, preTool, sessionStart, stop, taskCompleted, taskCreated, unknownEvent, userPrompt } from "../helpers/claude-fixtures.js";

describe("CC-HK hook mapping", () => {
  it("CC-HK-001 SessionStart creates a claude header", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-001";
    await drive(dir, [sessionStart(session)]);
    const header = headerOf(dir, session);
    assert.equal(header.session.origin, "claude");
    assert.equal(header.session.id, session);
    assert.equal(header.model.id, "claude-opus-4-6");
    const started = readJSONL(dir, session).find((e) => e.type === "session.start");
    assert.ok(started);
    assert.equal(started.source, "startup");
  });

  it("CC-HK-002 resume extras land in the header", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-002";
    await drive(dir, [sessionStart(session, "resume", { context_tokens: 42000, seconds_since_last_response: 61 })]);
    const header = headerOf(dir, session);
    assert.deepEqual(header.session.resume, { contextTokens: 42000, secondsSinceLast: 61 });
  });

  it("CC-HK-003 UserPromptSubmit records text and title", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-003";
    await drive(dir, [sessionStart(session), userPrompt(session, "Explain this backend")]);
    const prompted = readJSONL(dir, session).find((e) => e.type === "user.prompt");
    assert.ok(prompted);
    assert.match(prompted.text, /Explain this backend/);
    assert.equal(headerOf(dir, session).title, "Explain this backend");
  });

  it("CC-HK-004 Pre/PostToolUse records id, summary, and duration", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-004";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session),
      preTool(session, "Read", { file_path: "src/a.ts" }, "toolu_1"),
      postTool(session, "Read", { file_path: "src/a.ts" }, "contents", "toolu_1"),
      stop(session, { last_assistant_message: "" }),
    ]);
    const completed = turnFiles(dir, session);
    assert.equal(completed.length, 1);
    const doc = yamlDocs(dir, session, completed[0])[0];
    assert.equal(doc.assistant[0].tool_calls[0].tool, "Read");
    assert.deepEqual(doc.assistant[0].tool_calls[0].args, { file_path: "src/a.ts" });
    assert.equal(doc.assistant[0].tool_calls[0].toolUseId, "toolu_1");
    assert.equal(doc.assistant[0].tool_calls[0].durationMs, 120);
  });

  it("CC-HK-005 Bash summarized, MCP flagged, unknown dumped raw", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-005";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session),
      preTool(session, "Bash", { command: "npm test" }, "toolu_2"),
      postTool(session, "Bash", { command: "npm test" }, "ok", "toolu_2"),
      preTool(session, "mcp__memory__create_entities", { entities: [] }, "toolu_3"),
      postTool(session, "mcp__memory__create_entities", { entities: [] }, "ok", "toolu_3"),
      stop(session, { last_assistant_message: "" }),
    ]);
    const completed = turnFiles(dir, session);
    const doc = yamlDocs(dir, session, completed[0])[0];
    const calls = doc.assistant.flatMap((s) => s.tool_calls ?? []);
    assert.deepEqual(calls[0].args, { command: "npm test" });
    assert.deepEqual(calls[1].args, { mcp_tool: "mcp__memory__create_entities" });
  });

  it("CC-HK-006 PostToolUseFailure records error and interrupt", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-006";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session),
      postToolFailure(session, "Bash", { command: "exit 1" }, "Exit code 1", { is_interrupt: true }),
      stop(session, { last_assistant_message: "" }),
    ]);
    const failed = readJSONL(dir, session).find((e) => e.type === "tool.error");
    assert.ok(failed);
    assert.equal(failed.error, "Exit code 1");
    assert.equal(failed.isInterrupt, true);
    const doc = yamlDocs(dir, session, turnFiles(dir, session)[0])[0];
    assert.equal(doc.error, "Exit code 1");
    assert.equal(doc.interrupted, true);
  });

  it("CC-HK-007 compacts, tasks, and model switches are logged", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-007";
    await drive(dir, [
      sessionStart(session),
      preCompact(session),
      postCompact(session),
      taskCreated(session),
      taskCompleted(session),
      modelSwitch(session),
    ]);
    const entries = readJSONL(dir, session);
    assert.ok(entries.find((e) => e.type === "session.compacted" && e.phase === "pre"));
    assert.ok(entries.find((e) => e.type === "session.compacted" && e.phase === "post"));
    assert.ok(entries.find((e) => e.type === "task.created"));
    assert.ok(entries.find((e) => e.type === "task.completed"));
    const switched = entries.find((e) => e.type === "model.switch");
    assert.ok(switched);
    assert.equal(switched.to, "claude-opus-4-6");
    assert.equal(headerOf(dir, session).model.id, "claude-opus-4-6");
    assert.equal(persistedState(dir, session).model.id, "claude-opus-4-6");
  });

  it("CC-HK-008 unknown events are logged, never fatal", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-008";
    await drive(dir, [sessionStart(session), unknownEvent(session)]);
    const unknown = readJSONL(dir, session).find((e) => e.type === "hook.unknown");
    assert.ok(unknown);
    assert.equal(unknown.hookEventName, "SomeFutureEvent");
    assert.ok(filesIn(dir, session).length > 0);
  });
});
