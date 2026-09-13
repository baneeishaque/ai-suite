// CL-HK edge cases (cf. LG-HK-061, LG-HK-062, LG-HK-066).
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { handle } from "../../lib/router.js";
import { postTool, taskCancel, taskComplete, taskStart, unknownHook, userPrompt } from "../helpers/cline-fixtures.js";
import { drive, filesIn, readJSONL, turnFiles, useTempWorkspace, withRoot } from "../helpers/cline-harness.js";

describe("CL-HK edge cases", () => {
  it("CL-HK-061 unknown hook ignored, no crash", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-edge-unknown";
    await handle(withRoot(dir, unknownHook(task)));
    const types = readJSONL(dir, task).map((e) => e.type);
    assert.ok(types.includes("hook.unknown"));
  });

  it("CL-HK-062 PostToolUse with no prior state lazy-inits", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-edge-lazy";
    await drive(dir, [postTool(task), taskComplete(task)]);
    assert.equal(turnFiles(dir, task).length, 1);
  });

  it("CL-HK-066 user-only turn writes no turn file", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-edge-useronly";
    await drive(dir, [taskStart(task), userPrompt(task), taskComplete(task)]);
    assert.equal(turnFiles(dir, task).length, 0);
    assert.ok(filesIn(dir, task).some((f) => f.startsWith("000-header-")));
  });

  it("CL-HK-067 cancel finalizes like complete", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-edge-cancel";
    await drive(dir, [taskStart(task), userPrompt(task), postTool(task), taskCancel(task)]);
    assert.equal(turnFiles(dir, task).length, 1);
    assert.ok(readJSONL(dir, task).some((e) => e.type === "task.cancel"));
  });

  it("CL-HK-068 failed tool records ERROR result, still logs", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-edge-fail";
    await drive(dir, [
      taskStart(task), userPrompt(task),
      postTool(task, "execute_command", { result: "boom", success: false }),
      taskComplete(task),
    ]);
    assert.equal(turnFiles(dir, task).length, 1);
  });
});
