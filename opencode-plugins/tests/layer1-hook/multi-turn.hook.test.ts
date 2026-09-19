import { describe, expect, test } from "bun:test"
import { useTempCwd, makePlugin, drive, LOG_BASE, filesIn, yamlDocs, readTurnsJSONL } from "../helpers/harness"
import { sessionCreated, msgUpdated, partUpdated, textPart, idle, disposed } from "../helpers/fixtures"
import { readFileSync } from "node:fs"
import { join } from "node:path"

describe("LG-HK-010 multi-turn", () => {
  useTempCwd()

  test("LG-HK-011 two turns produce 001 and 002 files with sequential numbering", async () => {
    const ses = "ses_test_multi_002"
    const p = await makePlugin()

    await drive(p, [sessionCreated(ses)])
    for (const i of [1, 2]) {
      await drive(p, [
        msgUpdated(`m-user-${i}`, "user", ses),
        partUpdated(`m-user-${i}`, ses, textPart(`question ${i}`)),
        msgUpdated(`m-assistant-${i}`, "assistant", ses),
        partUpdated(`m-assistant-${i}`, ses, textPart(`answer ${i}`)),
        idle(ses),
      ])
    }
    await drive(p, [disposed()])

    const dir = join(LOG_BASE, ses)
    const turnFiles = filesIn(dir).filter((f) => /^00\d-2026/.test(f))
    expect(turnFiles.length).toBe(2)
    expect(turnFiles[0]).toMatch(/^001-\d{4}-/)
    expect(turnFiles[1]).toMatch(/^002-\d{4}-/)

    const doc1 = yamlDocs(join(dir, turnFiles[0]))[0]
    const doc2 = yamlDocs(join(dir, turnFiles[1]))[0]
    expect(doc1.user.text).toBe("question 1")
    expect(doc2.user.text).toBe("question 2")

    const turns = readTurnsJSONL(LOG_BASE, ses)
    expect(turns.length).toBe(2)
    const state = JSON.parse(readFileSync(join(LOG_BASE, `${ses}.state.json`), "utf-8"))
    expect(typeof state.created).toBe("string")
    expect(state.created.length).toBeGreaterThan(0)
  })
})
