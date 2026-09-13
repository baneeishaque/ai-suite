// CL-CP completion harvest: TaskComplete result text, tag stripping,
// clineVersion provenance (cf. live payloads of conv_1789314397549_g5p0nil:
// result arrived in taskComplete.taskMetadata, model stayed unknown,
// clineVersion 4.1.17 was the only reliable provenance).
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { drive, filesIn, readJSONL, turnFiles, useTempWorkspace, yamlDocs } from "../helpers/cline-harness.js";
import { taskComplete, taskStart, userPrompt } from "../helpers/cline-fixtures.js";

const RESULT = "OK — I'm here and ready. What next?";

function completeWithResult(task, result = RESULT) {
  const p = taskComplete(task);
  p.taskComplete = { taskMetadata: { taskId: task, ulid: "", initialTask: "", result } };
  return p;
}

describe("CL-CP completion harvest", () => {
  it("CL-CP-001 TaskComplete result lands in jsonl and turn file", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-harvest-001";
    await drive(dir, [taskStart(task), userPrompt(task), completeWithResult(task)]);
    const done = readJSONL(dir, task).find((e) => e.type === "task.complete");
    assert.ok(done);
    assert.equal(done.result, RESULT);
    const completed = turnFiles(dir, task);
    assert.equal(completed.length, 1);
    const doc = yamlDocs(dir, task, completed[0])[0];
    assert.equal(doc.assistant[0].response, RESULT);
  });

  it("CL-CP-002 result recorded once even when turn already ends with it", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-harvest-002";
    await drive(dir, [taskStart(task), userPrompt(task), completeWithResult(task)]);
    const completed = turnFiles(dir, task);
    const doc = yamlDocs(dir, task, completed[0])[0];
    assert.equal(doc.assistant[0].response, RESULT);
    assert.ok(!doc.assistant[0].response.includes(RESULT + RESULT));
  });

  it("CL-CP-003 user_input tags stripped from turn text", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-harvest-003";
    const tagged = '<user_input mode="act">Do the thing</user_input>';
    await drive(dir, [taskStart(task, tagged), userPrompt(task, tagged), completeWithResult(task, "done")]);
    const completed = turnFiles(dir, task);
    const doc = yamlDocs(dir, task, completed[0])[0];
    assert.equal(doc.user.text, "Do the thing");
    assert.ok(!doc.user.text.includes("user_input"));
  });

  it("CL-CP-004 clineVersion recorded in header", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-harvest-004";
    const start = taskStart(task);
    start.clineVersion = "4.1.17";
    await drive(dir, [start, userPrompt(task), completeWithResult(task, "done")]);
    const headerFile = filesIn(dir, task).find((f) => f.startsWith("000-header-"));
    const header = yamlDocs(dir, task, headerFile)[0];
    assert.equal(header.cline_version, "4.1.17");
  });
});
