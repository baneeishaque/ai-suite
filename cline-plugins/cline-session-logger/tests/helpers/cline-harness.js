// Test harness for the Cline hooks logger (node:test).
// Each test gets a temp workspace dir; payloads carry workspaceRoots:[dir]
// so all artifacts land under <dir>/.cline/run-logs/<task>/ (hermetic, no
// chdir, no shared module state — handle() hydrates from disk every call).
import { mkdtempSync, rmSync, existsSync, readdirSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { loadAll } from "js-yaml";
import { handle } from "../../lib/router.js";

export function useTempWorkspace(t) {
  const dir = mkdtempSync(join(tmpdir(), "cline-logger-test-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  return dir;
}

export function withRoot(dir, payload) {
  return { ...payload, workspaceRoots: [dir] };
}

export async function drive(dir, events) {
  for (const e of events) await handle(withRoot(dir, e));
}

export function taskLogDir(dir, taskId) {
  return join(dir, ".cline", "run-logs", taskId);
}

export function filesIn(dir, taskId) {
  const d = taskLogDir(dir, taskId);
  return existsSync(d) ? readdirSync(d).sort() : [];
}

export function readJSONL(dir, taskId) {
  const f = join(taskLogDir(dir, taskId), `${taskId}.jsonl`);
  if (!existsSync(f)) return [];
  return readFileSync(f, "utf-8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
}

export function readTurnsJSONL(dir, taskId) {
  const f = join(taskLogDir(dir, taskId), `${taskId}.turns.jsonl`);
  if (!existsSync(f)) return [];
  return readFileSync(f, "utf-8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
}

export function turnFiles(dir, taskId, { pending = false } = {}) {
  return filesIn(dir, taskId).filter((f) =>
    pending ? /^\d{3}-pending-.*\.yaml$/.test(f) : /^\d{3}-(?!pending-|header-).*\.yaml$/.test(f));
}

export function yamlDocs(dir, taskId, file) {
  return loadAll(readFileSync(join(taskLogDir(dir, taskId), file), "utf-8"));
}
