import { mkdtempSync, rmSync, mkdirSync, writeFileSync, readFileSync, readdirSync, existsSync } from "node:fs"
import { join } from "node:path"
import { tmpdir } from "node:os"
import { loadAll } from "js-yaml"
import { beforeEach, afterEach } from "bun:test"
import { OpenCodeLogger } from "../../opencode-logger"
import type { HookEvent } from "./fixtures"

export const LOG_BASE = ".opencode/logs"

export let tmpDir = ""
let prevCwd = ""

export function useTempCwd() {
  beforeEach(() => {
    prevCwd = process.cwd()
    tmpDir = mkdtempSync(join(tmpdir(), "logger-test-"))
    process.chdir(tmpDir)
  })
  afterEach(() => {
    process.chdir(prevCwd)
    rmSync(tmpDir, { recursive: true, force: true })
  })
}

export type Plugin = { event: (input: { event: HookEvent }) => Promise<void> }

export async function makePlugin(): Promise<Plugin> {
  return (await OpenCodeLogger({} as never)) as Plugin
}

export async function drive(p: Plugin, events: HookEvent[]) {
  for (const e of events) await p.event({ event: e })
}

export function filesIn(dir: string): string[] {
  return existsSync(dir) ? readdirSync(dir).sort() : []
}

export function yamlDocs(file: string): Record<string, unknown>[] {
  return loadAll(readFileSync(file, "utf-8")) as Record<string, unknown>[]
}

export function readJSONL(sesDir: string, ses: string): Record<string, unknown>[] {
  const f = join(sesDir, `${ses}.jsonl`)
  if (!existsSync(f)) return []
  return readFileSync(f, "utf-8")
    .trim()
    .split("\n")
    .filter(Boolean)
    .map((l) => JSON.parse(l))
}

export function readTurnsJSONL(sesDir: string, ses: string): Record<string, unknown>[] {
  const f = join(sesDir, `${ses}.turns.jsonl`)
  if (!existsSync(f)) return []
  return readFileSync(f, "utf-8")
    .trim()
    .split("\n")
    .filter(Boolean)
    .map((l) => JSON.parse(l))
}

export function seedSession(ses: string, turnFiles: Record<string, string>) {
  const base = join(LOG_BASE, ses)
  mkdirSync(base, { recursive: true })
  writeFileSync(join(base, "000-header-2026-08-02T21-52-05-760Z.yaml"), `---\nsession:\n  id: ${ses}\n`)
  for (const [name, content] of Object.entries(turnFiles)) {
    writeFileSync(join(base, name), content)
  }
}

export function resumeChild(dir: string, ses: string): void {
  const r = Bun.spawnSync({
    cmd: [process.execPath, join(import.meta.dir, "resume-runner.ts"), "--dir", dir, "--session", ses],
    stdout: "pipe",
    stderr: "pipe",
  })
  if (r.exitCode !== 0) {
    throw new Error(`resume child failed (exit ${r.exitCode}): ${r.stderr?.toString() ?? ""}`)
  }
}
