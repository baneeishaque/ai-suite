// CP-HK hook mapping: Copilot hook events land in the session log.
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { drive, filesIn, headerOf, readJSONL, turnFiles, useTempWorkspace, yamlDocs } from "../helpers/copilot-harness.js";
import { postTool, preCompact, preTool, sessionStart, stop, unknownEvent, userPrompt } from "../helpers/copilot-fixtures.js";

describe("CP-HK hook mapping", () => {
  it("CP-HK-001 SessionStart creates a copilot header", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-001";
    await drive(dir, [sessionStart(session)]);
    const header = headerOf(dir, session);
    assert.equal(header.session.origin, "copilot");
    assert.equal(header.session.id, session);
    const started = readJSONL(dir, session).find((e) => e.type === "session.start");
    assert.ok(started);
    assert.equal(started.source, "new");
  });

  it("CP-HK-002 UserPromptSubmit records text and title", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-002";
    await drive(dir, [sessionStart(session), userPrompt(session, "Explain this backend")]);
    const started = readJSONL(dir, session).find((e) => e.type === "user.prompt");
    assert.ok(started);
    assert.match(started.text, /Explain this backend/);
    assert.equal(headerOf(dir, session).title, "Explain this backend");
  });

  it("CP-HK-003 Pre/PostToolUse records the tool call with summary", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-003";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session),
      preTool(session, "copilot_readFile", { filePath: "src/a.ts" }, "tool-9"),
      postTool(session, "copilot_readFile", { filePath: "src/a.ts" }, "contents", "tool-9"),
      stop(session),
    ]);
    const completed = turnFiles(dir, session);
    assert.equal(completed.length, 1);
    const doc = yamlDocs(dir, session, completed[0])[0];
    assert.equal(doc.assistant[0].tool_calls[0].tool, "copilot_readFile");
    assert.deepEqual(doc.assistant[0].tool_calls[0].args, { path: "src/a.ts" });
    assert.equal(doc.assistant[0].tool_calls[0].toolUseId, "tool-9");
  });

  it("CP-HK-004 terminal command summarized, unknown tool dumped raw", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-004";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session),
      preTool(session, "run_in_terminal", { command: "npm test" }, "tool-10"),
      postTool(session, "run_in_terminal", { command: "npm test" }, "ok", "tool-10"),
      preTool(session, "mystery_tool", { foo: "bar" }, "tool-11"),
      postTool(session, "mystery_tool", { foo: "bar" }, "done", "tool-11"),
      stop(session),
    ]);
    const completed = turnFiles(dir, session);
    const doc = yamlDocs(dir, session, completed[0])[0];
    const calls = doc.assistant.flatMap((s) => s.tool_calls ?? []);
    assert.deepEqual(calls[0].args, { command: "npm test" });
    assert.match(calls[1].args._raw, /"foo":"bar"/);
  });

  it("CP-HK-005 PreCompact stamps the header and logs the trigger", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-005";
    await drive(dir, [sessionStart(session), preCompact(session, "auto")]);
    assert.ok(headerOf(dir, session).session.compacted);
    const compacted = readJSONL(dir, session).find((e) => e.type === "session.compacted");
    assert.ok(compacted);
    assert.equal(compacted.trigger, "auto");
  });

  it("CP-HK-006 unknown events are logged, never fatal", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-hk-006";
    await drive(dir, [sessionStart(session), unknownEvent(session)]);
    const unknown = readJSONL(dir, session).find((e) => e.type === "hook.unknown");
    assert.ok(unknown);
    assert.equal(unknown.hookEventName, "SomeFutureEvent");
    assert.ok(filesIn(dir, session).length > 0);
  });
});
