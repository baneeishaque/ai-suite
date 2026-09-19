import { describe, expect, test } from "bun:test"
import { mkdtempSync, mkdirSync, rmSync, symlinkSync, readFileSync, readdirSync, existsSync, copyFileSync } from "node:fs"
import { join } from "node:path"
import { tmpdir } from "node:os"
import { MARKERS } from "../helpers/fixtures"

const E2E_RUN = process.env.E2E_RUN === "1"
const OPENCODE_BIN = process.env.OPENCODE_BIN ?? "opencode"
const E2E_PROMPT = process.env.E2E_PROMPT ?? MARKERS.e2ePrompt
const ARTIFACTS = join(import.meta.dir, "..", "e2e-artifacts")

describe("LG-E2-001 real opencode E2E", () => {
  test("LG-E2-002 plugin loaded by real binary writes session logs with marker", async () => {
    if (!E2E_RUN) {
      console.log("E2E skipped (set E2E_RUN=1 to execute; needs a real opencode binary)")
      return
    }

    const tmp = mkdtempSync(join(tmpdir(), "logger-e2e-"))
    const pluginsDir = join(tmp, ".opencode", "plugins")
    mkdirSync(pluginsDir, { recursive: true })
    symlinkSync(join(import.meta.dir, "..", "..", "opencode-logger.ts"), join(pluginsDir, "opencode-logger.ts"))

    const r = Bun.spawnSync({
      cmd: [OPENCODE_BIN, "run", E2E_PROMPT],
      cwd: tmp,
      stdout: "pipe",
      stderr: "pipe",
      timeout: 240_000,
    })

    const logsDir = join(tmp, ".opencode", "logs")
    let sessionDirs: string[] = []
    if (existsSync(logsDir)) {
      sessionDirs = readdirSync(logsDir).filter((f) => f.startsWith("ses_"))
    }

    if (r.exitCode !== 0 || sessionDirs.length === 0) {
      mkdirSync(ARTIFACTS, { recursive: true })
      if (sessionDirs.length > 0) {
        const jsonl = join(logsDir, `${sessionDirs[0]}.jsonl`)
        if (existsSync(jsonl)) {
          try { copyFileSync(jsonl, join(ARTIFACTS, "e2e-failure.jsonl")) } catch { /* best effort */ }
        }
      }
      rmSync(tmp, { recursive: true, force: true })
      expect(r.exitCode, `opencode run failed (exit ${r.exitCode}) stderr: ${r.stderr?.toString() ?? ""}`).toBe(0)
      expect(sessionDirs.length).toBeGreaterThan(0)
    }

    const sesDir = join(logsDir, sessionDirs[0])
    const files = readdirSync(sesDir)
    expect(files.some((f) => f.startsWith("000-header-"))).toBe(true)
    expect(files.some((f) => /^\d{3}-\d{4}/.test(f))).toBe(true)
    const turnFile = files.find((f) => /^\d{3}-\d{4}/.test(f))!
    const content = readFileSync(join(sesDir, turnFile), "utf-8")
    expect(content).toContain("E2E-LOGGER-OK")

    rmSync(tmp, { recursive: true, force: true })
  }, 240_000)
})
