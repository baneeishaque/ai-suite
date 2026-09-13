// CL-HK-070 shim launcher: the real extensionless executables must work when
// spawned with a GUI-like minimal PATH (VS Code from Dock/Finder has no node
// on PATH). Regression test for "hooks enabled but no YAML".
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, readdirSync, symlinkSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";

const HOOKS_DIR = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "hooks");
const GUI_PATH = "/usr/bin:/bin:/usr/sbin:/sbin";

function runShim(name, payload, workspace) {
  return spawnSync(join(HOOKS_DIR, name), {
    input: JSON.stringify({ ...payload, workspaceRoots: [workspace] }),
    encoding: "utf-8",
    cwd: HOOKS_DIR,
    env: { ...process.env, PATH: GUI_PATH, HOME: process.env.HOME ?? "" },
    timeout: 15000,
  });
}

describe("CL-HK shim launcher", () => {
  it("CL-HK-070 TaskStart works under GUI-like minimal PATH", (t) => {
    const workspace = mkdtempSync(join(tmpdir(), "cline-shim-test-"));
    t.after(() => {});
    const task = "shim-probe-1";
    const base = {
      taskId: task,
      timestamp: String(Date.now()),
      userId: "u",
      model: { provider: "anthropic", slug: "claude-sonnet-4-5" },
    };
    const r = runShim("TaskStart", { ...base, hookName: "TaskStart", taskStart: { task: "probe" } }, workspace);
    assert.equal(r.status, 0, `stderr: ${r.stderr}`);
    assert.equal(r.stdout.trim(), '{"cancel":false}');
    const dir = join(workspace, ".cline", "run-logs", task);
    assert.ok(existsSync(dir), `log dir missing; files: ${readdirSync(workspace)}`);
    assert.ok(readdirSync(dir).some((f) => f.startsWith("000-header-")));
  });

  it("CL-HK-071 TaskStart works when invoked via symlink (global-install path)", (t) => {
    const workspace = mkdtempSync(join(tmpdir(), "cline-shim-test-"));
    const linkDir = mkdtempSync(join(tmpdir(), "cline-shim-links-"));
    t.after(() => {});
    const task = "shim-probe-2";
    const link = join(linkDir, "TaskStart");
    symlinkSync(join(HOOKS_DIR, "TaskStart"), link);
    const base = {
      taskId: task,
      timestamp: String(Date.now()),
      userId: "u",
      model: { provider: "anthropic", slug: "claude-sonnet-4-5" },
    };
    const r = spawnSync(link, {
      input: JSON.stringify({ ...base, hookName: "TaskStart", taskStart: { task: "probe" }, workspaceRoots: [workspace] }),
      encoding: "utf-8",
      cwd: linkDir,
      env: { ...process.env, PATH: GUI_PATH, HOME: process.env.HOME ?? "" },
      timeout: 15000,
    });
    assert.equal(r.status, 0, `stderr: ${r.stderr}`);
    assert.equal(r.stdout.trim(), '{"cancel":false}');
    const dir = join(workspace, ".cline", "run-logs", task);
    assert.ok(existsSync(dir), "log dir missing via symlink invocation");
    assert.ok(readdirSync(dir).some((f) => f.startsWith("000-header-")));
  });
});
