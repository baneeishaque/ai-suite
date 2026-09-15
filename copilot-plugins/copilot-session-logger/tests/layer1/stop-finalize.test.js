// CP-STOP session stop: Stop finalizes the turn and logs session.stop.
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { drive, readJSONL, turnFiles, useTempWorkspace, yamlDocs } from "../helpers/copilot-harness.js";
import { postTool, preTool, sessionStart, stop, userPrompt } from "../helpers/copilot-fixtures.js";

describe("CP-STOP session stop", () => {
  it("CP-STOP-001 Stop finalizes the turn and logs session.stop", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-stop-001";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session, "Write tests"),
      preTool(session, "copilot_createFile", { filePath: "test/a.test.js" }, "tool-30"),
      postTool(session, "copilot_createFile", { filePath: "test/a.test.js" }, "created", "tool-30"),
      stop(session),
    ]);
    const completed = turnFiles(dir, session);
    assert.equal(completed.length, 1);
    const doc = yamlDocs(dir, session, completed[0])[0];
    assert.equal(doc.user.text, "Write tests");
    assert.equal(doc.assistant[0].tool_calls[0].tool, "copilot_createFile");
    const stopped = readJSONL(dir, session).find((e) => e.type === "session.stop");
    assert.ok(stopped);
    assert.equal(stopped.stopHookActive, false);
  });

  it("CP-STOP-002 Stop with no turn still logs session.stop", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-stop-002";
    await drive(dir, [sessionStart(session), stop(session)]);
    assert.equal(turnFiles(dir, session).length, 0);
    assert.ok(readJSONL(dir, session).find((e) => e.type === "session.stop"));
  });
});
