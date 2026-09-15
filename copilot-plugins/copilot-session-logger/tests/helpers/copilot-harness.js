// Test harness for the Copilot hooks logger (node:test).
// Each test gets a temp workspace dir; payloads carry cwd = dir
// so all artifacts land under <dir>/.copilot/run-logs/<session>/
// (hermetic — handle() hydrates from disk every call).
import { mkdtempSync, rmSync, existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { loadAll } from "js-yaml";
import { handle } from "../../lib/router.js";

export function useTempWorkspace(t) {
  const dir = mkdtempSync(join(tmpdir(), "copilot-logger-test-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  return dir;
}

export function withCwd(dir, payload) {
  return { ...payload, cwd: payload.cwd || dir };
}

export async function drive(dir, events) {
  for (const e of events) await handle(withCwd(dir, e));
}

export function writeTranscript(dir, name, data) {
  const p = join(dir, name);
  writeFileSync(p, JSON.stringify(data));
  return p;
}

export function writeTranscriptText(dir, name, text) {
  const p = join(dir, name);
  writeFileSync(p, text);
  return p;
}

export function sessionLogDir(dir, sessionId) {
  return join(dir, ".copilot", "run-logs", sessionId);
}

export function filesIn(dir, sessionId) {
  const d = sessionLogDir(dir, sessionId);
  return existsSync(d) ? readdirSync(d).sort() : [];
}

export function readJSONL(dir, sessionId) {
  const f = join(sessionLogDir(dir, sessionId), `${sessionId}.jsonl`);
  if (!existsSync(f)) return [];
  return readFileSync(f, "utf-8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
}

export function readTurnsJSONL(dir, sessionId) {
  const f = join(sessionLogDir(dir, sessionId), `${sessionId}.turns.jsonl`);
  if (!existsSync(f)) return [];
  return readFileSync(f, "utf-8").trim().split("\n").filter(Boolean).map((l) => JSON.parse(l));
}

export function turnFiles(dir, sessionId, { pending = false } = {}) {
  return filesIn(dir, sessionId).filter((f) =>
    pending ? /^\d{3}-pending-.*\.yaml$/.test(f) : /^\d{3}-(?!pending-|header-).*\.yaml$/.test(f));
}

export function yamlDocs(dir, sessionId, file) {
  return loadAll(readFileSync(join(sessionLogDir(dir, sessionId), file), "utf-8"));
}

export function headerOf(dir, sessionId) {
  const headerFile = filesIn(dir, sessionId).find((f) => f.startsWith("000-header-"));
  if (!headerFile) throw new Error("no header file");
  return yamlDocs(dir, sessionId, headerFile)[0];
}

export function persistedState(dir, sessionId) {
  return JSON.parse(readFileSync(join(sessionLogDir(dir, sessionId), "state.json"), "utf-8"));
}
