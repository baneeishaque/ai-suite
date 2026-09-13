// CL-RC recovery: resume without duplication + orphan pending not promoted
// (cf. LG-RC-011 clean history, LG-RC-002 orphan pending — fixed semantics:
// pending files are evidence only, never promoted to completed turns).
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { MARKERS, postTool, preTool, taskComplete, taskResume, taskStart, userPrompt } from "../helpers/cline-fixtures.js";
import { drive, readTurnsJSONL, taskLogDir, turnFiles, useTempWorkspace, yamlDocs } from "../helpers/cline-harness.js";

describe("CL-RC recovery", () => {
  it("CL-RC-011 resume continues numbering, no duplicates", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-recovery-001";
    // First "process": one completed turn (each handle() hydrates from disk,
    // so every call already simulates a fresh process).
    await drive(dir, [taskStart(task), userPrompt(task), preTool(task), postTool(task), taskComplete(task)]);
    assert.equal(turnFiles(dir, task).length, 1);
    // "Restart": resume + second turn.
    await drive(dir, [
      taskResume(task), userPrompt(task, MARKERS.secondUserText),
      preTool(task), postTool(task), taskComplete(task),
    ]);
    const completed = turnFiles(dir, task);
    assert.equal(completed.length, 2);
    assert.equal(readTurnsJSONL(dir, task).length, 2);
    assert.equal(yamlDocs(dir, task, completed[1])[0].user.text, MARKERS.secondUserText);
  });

  it("CL-RC-002 orphan pending file is never promoted", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-recovery-orphan";
    const logDir = taskLogDir(dir, task);
    mkdirSync(logDir, { recursive: true });
    // Seed a crashed-session pending file + minimal state (no liveTurn).
    writeFileSync(join(logDir, "001-pending-2026-09-13T00-00-00-000Z.yaml"), "---\nuser:\n  text: orphan\n");
    writeFileSync(join(logDir, "state.json"), JSON.stringify({ created: new Date().toISOString(), writtenTurns: 0 }));
    // Fresh work after the crash starts numbering at 001; orphan untouched.
    await drive(dir, [taskStart(task), userPrompt(task), preTool(task), postTool(task), taskComplete(task)]);
    const completed = turnFiles(dir, task);
    assert.equal(completed.length, 1);
    assert.equal(yamlDocs(dir, task, completed[0])[0].user.text, MARKERS.userText);
    assert.equal(turnFiles(dir, task, { pending: true }).filter((f) => f.includes("2026-09-13")).length, 1);
  });
});
