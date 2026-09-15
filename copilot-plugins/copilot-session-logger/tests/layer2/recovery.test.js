// CP-RC recovery: state round-trips across hook processes; numbering
// resumes without duplicates; subagent brackets survive processes.
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { drive, persistedState, turnFiles, useTempWorkspace } from "../helpers/copilot-harness.js";
import { postTool, preTool, sessionStart, stop, subagentStart, subagentStop, userPrompt } from "../helpers/copilot-fixtures.js";

describe("CP-RC recovery", () => {
  it("CP-RC-001 pending tool survives across hook processes", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-rc-001";
    await drive(dir, [sessionStart(session), userPrompt(session)]);
    await drive(dir, [preTool(session, "copilot_readFile", { filePath: "src/a.ts" }, "tool-40")]);
    const mid = persistedState(dir, session);
    assert.equal(mid.liveTurn.steps[0].pendingTool, "copilot_readFile");
    await drive(dir, [postTool(session, "copilot_readFile", { filePath: "src/a.ts" }, "contents", "tool-40")]);
    await drive(dir, [stop(session)]);
    assert.equal(turnFiles(dir, session).length, 1);
  });

  it("CP-RC-002 resume continues numbering, no duplicates", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-rc-002";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session, "First"),
      preTool(session, "copilot_readFile", { filePath: "src/a.ts" }, "tool-42"),
      postTool(session, "copilot_readFile", { filePath: "src/a.ts" }, "a", "tool-42"),
    ]);
    await drive(dir, [stop(session)]);
    await drive(dir, [
      userPrompt(session, "Second"),
      preTool(session, "copilot_readFile", { filePath: "src/b.ts" }, "tool-43"),
      postTool(session, "copilot_readFile", { filePath: "src/b.ts" }, "b", "tool-43"),
    ]);
    await drive(dir, [stop(session)]);
    assert.equal(turnFiles(dir, session).length, 2);
  });

  it("CP-RC-003 subagent bracket survives across hook processes", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-rc-003";
    await drive(dir, [sessionStart(session), subagentStart(session, "subagent-9", "Search")]);
    await drive(dir, [preTool(session, "copilot_findFiles", { query: "*.md" }, "tool-41")]);
    await drive(dir, [postTool(session, "copilot_findFiles", { query: "*.md" }, "README.md", "tool-41")]);
    const mid = persistedState(dir, session);
    assert.equal(mid.activeSubagent, "subagent-9");
    assert.equal(mid.subTurns["subagent-9"].steps[0].toolCalls[0].tool, "copilot_findFiles");
    await drive(dir, [subagentStop(session, "subagent-9")]);
    assert.equal(turnFiles(dir, session).length, 1);
  });
});
