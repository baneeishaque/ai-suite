// CC-RC recovery: state round-trips across hook processes; numbering
// resumes without duplicates; subagent brackets survive processes.
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { drive, persistedState, turnFiles, useTempWorkspace } from "../helpers/claude-harness.js";
import { postTool, preTool, sessionStart, stop, subagentStart, subagentStop, userPrompt } from "../helpers/claude-fixtures.js";

describe("CC-RC recovery", () => {
  it("CC-RC-001 pending tool survives across hook processes", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-rc-001";
    await drive(dir, [sessionStart(session), userPrompt(session)]);
    await drive(dir, [preTool(session, "Read", { file_path: "src/a.ts" }, "toolu_40")]);
    const mid = persistedState(dir, session);
    assert.equal(mid.liveTurn.steps[0].pendingTool, "Read");
    await drive(dir, [postTool(session, "Read", { file_path: "src/a.ts" }, "contents", "toolu_40")]);
    await drive(dir, [stop(session, { last_assistant_message: "" })]);
    assert.equal(turnFiles(dir, session).length, 1);
  });

  it("CC-RC-002 resume continues numbering, no duplicates", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-rc-002";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session, "First"),
      preTool(session, "Read", { file_path: "src/a.ts" }, "toolu_42"),
      postTool(session, "Read", { file_path: "src/a.ts" }, "a", "toolu_42"),
    ]);
    await drive(dir, [stop(session, { last_assistant_message: "" })]);
    await drive(dir, [
      userPrompt(session, "Second"),
      preTool(session, "Read", { file_path: "src/b.ts" }, "toolu_43"),
      postTool(session, "Read", { file_path: "src/b.ts" }, "b", "toolu_43"),
    ]);
    await drive(dir, [stop(session, { last_assistant_message: "" })]);
    assert.equal(turnFiles(dir, session).length, 2);
  });

  it("CC-RC-003 subagent bracket survives across hook processes", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-rc-003";
    await drive(dir, [sessionStart(session), subagentStart(session, "agent-9", "Explore")]);
    await drive(dir, [preTool(session, "Glob", { pattern: "*.md" }, "toolu_41")]);
    await drive(dir, [postTool(session, "Glob", { pattern: "*.md" }, "README.md", "toolu_41")]);
    const mid = persistedState(dir, session);
    assert.equal(mid.activeSubagent, "agent-9");
    assert.equal(mid.subTurns["agent-9"].steps[0].toolCalls[0].tool, "Glob");
    await drive(dir, [subagentStop(session, "agent-9", "Explore")]);
    assert.equal(turnFiles(dir, session).length, 1);
  });
});
