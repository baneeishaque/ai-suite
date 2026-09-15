// CL-TID taskMetadata identity harvest: ulid, *Id spillover, userId
// (forward-only: IDs recorded from TaskStart, refreshed on TaskComplete).
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { drive, filesIn, readJSONL, taskLogDir, useTempWorkspace, yamlDocs } from "../helpers/cline-harness.js";
import { postTool, preTool, taskComplete, taskStart, userPrompt } from "../helpers/cline-fixtures.js";

function headerOf(dir, task) {
  const headerFile = filesIn(dir, task).find((f) => f.startsWith("000-header-"));
  assert.ok(headerFile);
  return yamlDocs(dir, task, headerFile)[0];
}

function persistedState(dir, task) {
  return JSON.parse(readFileSync(join(taskLogDir(dir, task), "state.json"), "utf-8"));
}

describe("CL-TID taskMetadata identity harvest", () => {
  it("CL-TID-001 TaskStart ulid + *Id spillover land in header and state", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-ids-001";
    await drive(dir, [taskStart(task, "test task", { ulid: "01J0000000000000000000001", extraIds: { parentTaskId: "parent-001" } })]);
    const header = headerOf(dir, task);
    assert.equal(header.session.ulid, "01J0000000000000000000001");
    assert.deepEqual(header.session.task_ids, { taskId: task, ulid: "01J0000000000000000000001", parentTaskId: "parent-001" });
    const state = persistedState(dir, task);
    assert.equal(state.ulid, "01J0000000000000000000001");
    assert.deepEqual(state.taskIds, { taskId: task, ulid: "01J0000000000000000000001", parentTaskId: "parent-001" });
  });

  it("CL-TID-002 IDs survive across separate hook processes", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-ids-002";
    await drive(dir, [
      taskStart(task, "test task", { ulid: "01J0000000000000000000002" }),
      userPrompt(task),
      preTool(task),
      postTool(task),
      taskComplete(task),
    ]);
    const header = headerOf(dir, task);
    assert.equal(header.session.ulid, "01J0000000000000000000002");
    const done = readJSONL(dir, task).find((e) => e.type === "task.complete");
    assert.ok(done);
    assert.equal(done.ulid, "01J0000000000000000000002");
    assert.deepEqual(done.taskIds, { taskId: task, ulid: "01J0000000000000000000002" });
  });

  it("CL-TID-003 TaskComplete backfills IDs missing at TaskStart", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-ids-003";
    await drive(dir, [
      taskStart(task),
      taskComplete(task, { taskMetadata: { taskId: task, ulid: "01J0000000000000000000003", result: "done" } }),
    ]);
    const header = headerOf(dir, task);
    assert.equal(header.session.ulid, "01J0000000000000000000003");
  });

  it("CL-TID-004 userId lands in header and task.start JSONL", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-ids-004";
    const start = taskStart(task);
    start.userId = "user-abc-123";
    await drive(dir, [start]);
    const header = headerOf(dir, task);
    assert.equal(header.session.user_id, "user-abc-123");
    const started = readJSONL(dir, task).find((e) => e.type === "task.start");
    assert.ok(started);
    assert.equal(started.userId, "user-abc-123");
  });

  it("CL-TID-005 missing IDs leave the header clean", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-ids-005";
    const start = taskStart(task);
    delete start.taskStart.taskMetadata;
    delete start.userId;
    await drive(dir, [start]);
    const header = headerOf(dir, task);
    assert.ok(!("ulid" in header.session));
    assert.ok(!("task_ids" in header.session));
    assert.ok(!("user_id" in header.session));
  });
});
