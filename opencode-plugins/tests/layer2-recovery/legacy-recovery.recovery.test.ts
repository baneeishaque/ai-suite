import { describe, expect, test } from "bun:test"
import { useTempCwd, makePlugin, drive, LOG_BASE, filesIn, yamlDocs } from "../helpers/harness"
import { sessionCreated, msgUpdated, partUpdated, textPart, idle, disposed } from "../helpers/fixtures"
import { mkdirSync, writeFileSync } from "node:fs"
import { join } from "node:path"

describe("LG-RC-020 legacy flat-file recovery", () => {
  useTempCwd()

  test("LG-RC-021 resume from legacy flat 000-YYYY-MM-DD-HH-mm.yaml + NNN-pending files", async () => {
    const ses = "ses_test_legacy_022"
    const base = join(LOG_BASE, ses)
    mkdirSync(base, { recursive: true })
    writeFileSync(join(base, "000-2026-08-02T21-52-05-760Z.yaml"), "---\nsession:\n  id: " + ses + "\n")
    writeFileSync(join(base, "001-pending-2026-08-02T21-52-05-760Z.yaml"), "---\nuser:\n  text: legacy turn\n")

    const p = await makePlugin()
    await drive(p, [sessionCreated(ses), msgUpdated("m-u", "user", ses), partUpdated("m-u", ses, textPart("second")), idle(ses), disposed()])

    const after = filesIn(base)
    expect(after.some((f) => /^000-2026/.test(f))).toBe(true)
    expect(after.filter((f) => f.includes("pending"))).toEqual([])
    const newTurn = after.find((f) => /^00\d-2026/.test(f) && !f.includes("pending") && !f.startsWith("000-"))!
    const doc = yamlDocs(join(base, newTurn))[0]
    expect(doc.user.text).toBe("second")
  })
})
