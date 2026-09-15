// CC-STOP/CC-END turn close: Stop attaches last_assistant_message,
// StopFailure records the error, SessionEnd stamps the true close reason.
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { drive, headerOf, readJSONL, turnFiles, useTempWorkspace, yamlDocs } from "../helpers/claude-harness.js";
import { postTool, preTool, sessionEnd, sessionStart, stop, stopFailure, subagentStart, userPrompt } from "../helpers/claude-fixtures.js";

describe("CC-STOP turn close", () => {
  it("CC-STOP-001 Stop attaches the final text without transcript", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-stop-001";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session, "Write tests"),
      preTool(session, "Write", { file_path: "test/a.test.js" }, "toolu_30"),
      postTool(session, "Write", { file_path: "test/a.test.js" }, "created", "toolu_30"),
      stop(session),
    ]);
    const completed = turnFiles(dir, session);
    assert.equal(completed.length, 1);
    const doc = yamlDocs(dir, session, completed[0])[0];
    assert.equal(doc.assistant[0].response, "Done, all green.");
    const stopped = readJSONL(dir, session).find((e) => e.type === "turn.stop");
    assert.ok(stopped);
    assert.equal(stopped.stopHookActive, false);
  });

  it("CC-STOP-002 tool-less ping still produces a turn file", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-stop-002";
    await drive(dir, [sessionStart(session), userPrompt(session, "Ping"), stop(session)]);
    const completed = turnFiles(dir, session);
    assert.equal(completed.length, 1);
    const doc = yamlDocs(dir, session, completed[0])[0];
    assert.equal(doc.assistant[0].response, "Done, all green.");
  });

  it("CC-STOP-003 repeated Stop never duplicates the response", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-stop-003";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session, "Ping"),
      stop(session),
      stop(session),
    ]);
    const completed = turnFiles(dir, session);
    assert.equal(completed.length, 1);
    const doc = yamlDocs(dir, session, completed[0])[0];
    assert.equal(doc.assistant.length, 1);
  });

  it("CC-STOP-004 StopFailure records the error", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-stop-004";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session, "Do it"),
      preTool(session, "Bash", { command: "exit 1" }, "toolu_31"),
      postTool(session, "Bash", { command: "exit 1" }, "failed", "toolu_31"),
      stopFailure(session),
    ]);
    const failed = readJSONL(dir, session).find((e) => e.type === "turn.failed" && "error" in e);
    assert.ok(failed);
    assert.equal(failed.error, "rate_limit");
    const doc = yamlDocs(dir, session, turnFiles(dir, session)[0])[0];
    assert.equal(doc.error, "rate_limit");
  });
});

describe("CC-END session end", () => {
  it("CC-END-001 SessionEnd stamps the reason and flushes", async (t) => {
    const dir = useTempWorkspace(t);
    const session = "sess-end-001";
    await drive(dir, [
      sessionStart(session),
      userPrompt(session, "Quick task"),
      subagentStart(session, "agent-7", "Explore"),
      sessionEnd(session, "logout"),
    ]);
    const ended = readJSONL(dir, session).find((e) => e.type === "session.end");
    assert.ok(ended);
    assert.equal(ended.reason, "logout");
    assert.equal(headerOf(dir, session).session.end_reason, "logout");
  });
});
