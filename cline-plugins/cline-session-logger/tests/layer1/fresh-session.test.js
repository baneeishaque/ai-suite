// CL-HK fresh session + multi-turn numbering (cf. LG-HK-002, LG-HK-011).
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { MARKERS, postTool, preTool, taskComplete, taskStart, userPrompt } from "../helpers/cline-fixtures.js";
import { drive, filesIn, readJSONL, readTurnsJSONL, turnFiles, useTempWorkspace, yamlDocs } from "../helpers/cline-harness.js";

describe("CL-HK fresh session", () => {
  it("CL-HK-002 single turn writes header + 001 + jsonl", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-fresh-001";
    await drive(dir, [taskStart(task), userPrompt(task), preTool(task), postTool(task), taskComplete(task)]);

    const files = filesIn(dir, task);
    assert.ok(files.some((f) => f.startsWith("000-header-")), `header missing: ${files}`);
    assert.equal(turnFiles(dir, task).length, 1);

    const [header] = yamlDocs(dir, task, files.find((f) => f.startsWith("000-header-")));
    assert.equal(header.session.id, task);
    assert.equal(header.session.origin, "cline");
    assert.equal(header.model.id, "claude-sonnet-4-5");

    const turnDoc = yamlDocs(dir, task, turnFiles(dir, task)[0])[0];
    assert.equal(turnDoc.user.text, MARKERS.userText);
    assert.equal(turnDoc.assistant[0].tool_calls[0].tool, "read_file");

    const types = readJSONL(dir, task).map((e) => e.type);
    for (const want of ["task.start", "user.prompt", "tool.call", "tool.result", "turn.complete", "task.complete"]) {
      assert.ok(types.includes(want), `jsonl missing ${want}: ${types}`);
    }
    assert.equal(readTurnsJSONL(dir, task).length, 1);
  });

  it("CL-HK-011 two turns number 001 + 002", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-multi-001";
    await drive(dir, [
      taskStart(task), userPrompt(task, MARKERS.userText), preTool(task), postTool(task),
      userPrompt(task, MARKERS.secondUserText), preTool(task, "write_to_file", { path: "b.ts" }),
      postTool(task, "write_to_file", { parameters: { path: "b.ts" } }), taskComplete(task),
    ]);
    assert.equal(turnFiles(dir, task).length, 2);
    assert.equal(readTurnsJSONL(dir, task).length, 2);
    const docs = turnFiles(dir, task).map((f) => yamlDocs(dir, task, f)[0]);
    assert.equal(docs[0].user.text, MARKERS.userText);
    assert.equal(docs[1].user.text, MARKERS.secondUserText);
  });
});
