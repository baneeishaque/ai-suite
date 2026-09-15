// CP-SUB nested subagents: tool calls inside a SubagentStart..Stop
// bracket land in a nested subagent turn doc.
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { drive, persistedState, readJSONL, turnFiles, useTempWorkspace, yamlDocs } from "../helpers/copilot-harness.js";
import { postTool, preTool, sessionStart, stop, subagentStart, subagentStop, userPrompt } from "../helpers/copilot-fixtures.js";

describe("CP-SUB nested subagents", () => {
  it("CP-SUB-001 bracketed tool calls land in a subagent doc", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-sub-001";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session, "Refactor this"),
      subagentStart(session, "subagent-1", "Plan"),
      preTool(session, "copilot_findFiles", { query: "*.ts" }, "tool-20"),
      postTool(session, "copilot_findFiles", { query: "*.ts" }, "a.ts", "tool-20"),
      subagentStop(session, "subagent-1"),
    ]);
    const completed = turnFiles(dir, session);
    assert.equal(completed.length, 1);
    const doc = yamlDocs(dir, session, completed[0])[0];
    assert.deepEqual(doc.subagent, { id: "subagent-1", type: "Plan" });
    assert.equal(doc.assistant[0].tool_calls[0].tool, "copilot_findFiles");
    const state = persistedState(dir, session);
    assert.equal(state.activeSubagent, null);
    assert.deepEqual(state.subTurns, {});
  });

  it("CP-SUB-002 parent turn keeps its own content", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-sub-002";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session, "Parent task"),
      preTool(session, "copilot_readFile", { filePath: "src/main.ts" }, "tool-21"),
      postTool(session, "copilot_readFile", { filePath: "src/main.ts" }, "code", "tool-21"),
      subagentStart(session, "subagent-2", "Search"),
      preTool(session, "copilot_findTextInFiles", { query: "foo" }, "tool-22"),
      postTool(session, "copilot_findTextInFiles", { query: "foo" }, "hit", "tool-22"),
      subagentStop(session, "subagent-2"),
      stop(session),
    ]);
    const completed = turnFiles(dir, session);
    assert.equal(completed.length, 2);
    const sub = yamlDocs(dir, session, completed[0])[0];
    const parent = yamlDocs(dir, session, completed[1])[0];
    assert.ok(sub.subagent);
    assert.ok(!parent.subagent);
    assert.equal(parent.assistant[0].tool_calls[0].tool, "copilot_readFile");
  });

  it("CP-SUB-003 Stop flushes a still-open bracket", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-sub-003";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session, "Do it"),
      subagentStart(session, "subagent-3", "Plan"),
      preTool(session, "copilot_listDirectory", { path: "src" }, "tool-23"),
      postTool(session, "copilot_listDirectory", { path: "src" }, "a.ts", "tool-23"),
      stop(session),
    ]);
    const completed = turnFiles(dir, session);
    assert.ok(completed.length >= 1);
    const first = yamlDocs(dir, session, completed[0])[0];
    assert.deepEqual(first.subagent, { id: "subagent-3", type: "Plan" });
    const stopped = readJSONL(dir, session).find((e) => e.type === "session.stop");
    assert.ok(stopped);
  });
});
