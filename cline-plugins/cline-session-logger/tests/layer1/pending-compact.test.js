// CL-HK pending lifecycle + precompact (cf. LG-HK-021, LG-HK-051).
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { handle } from "../../lib/router.js";
import { postTool, preCompact, preTool, taskComplete, taskStart, userPrompt } from "../helpers/cline-fixtures.js";
import { drive, filesIn, readJSONL, turnFiles, useTempWorkspace, withRoot, yamlDocs } from "../helpers/cline-harness.js";

describe("CL-HK pending + compact", () => {
  it("CL-HK-021 pending file exists after tool, replaced on complete", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-pending-001";
    await drive(dir, [taskStart(task), userPrompt(task), preTool(task), postTool(task)]);
    const pend = turnFiles(dir, task, { pending: true });
    assert.equal(pend.length, 1);
    assert.equal(turnFiles(dir, task).length, 0);

    await handle(withRoot(dir, taskComplete(task)));
    assert.equal(turnFiles(dir, task, { pending: true }).length, 0);
    assert.equal(turnFiles(dir, task).length, 1);
  });

  it("CL-HK-051 precompact marks header + jsonl, numbering continues", async (t) => {
    const dir = useTempWorkspace(t);
    const task = "task-compact-001";
    await drive(dir, [taskStart(task), userPrompt(task), preTool(task), postTool(task), preCompact(task)]);
    const types = readJSONL(dir, task).map((e) => e.type);
    assert.ok(types.includes("task.compacted"));
    const headerFile = filesIn(dir, task).find((f) => f.startsWith("000-header-"));
    const header = yamlDocs(dir, task, headerFile)[0];
    assert.ok(header.session.compacted, "header missing compacted");

    await drive(dir, [userPrompt(task, "after compact"), preTool(task), postTool(task), taskComplete(task)]);
    assert.equal(turnFiles(dir, task).length, 2);
  });
});
