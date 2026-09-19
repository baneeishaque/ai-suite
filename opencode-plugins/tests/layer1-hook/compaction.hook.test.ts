import { describe, expect, test } from "bun:test"
import { useTempCwd, makePlugin, drive, LOG_BASE, filesIn, readJSONL } from "../helpers/harness"
import { sessionCreated, msgUpdated, partUpdated, textPart, idle, compacted, disposed } from "../helpers/fixtures"
import { join } from "node:path"

describe("LG-HK-050 compaction", () => {
  useTempCwd()

  test("LG-HK-051 compaction between turns is logged and numbering continues", async () => {
    const ses = "ses_test_compact_011"
    const p = await makePlugin()

    await drive(p, [
      sessionCreated(ses),
      msgUpdated("m-u1", "user", ses),
      partUpdated("m-u1", ses, textPart("q1")),
      msgUpdated("m-a1", "assistant", ses),
      partUpdated("m-a1", ses, textPart("a1")),
      idle(ses),
      compacted(ses),
      msgUpdated("m-u2", "user", ses),
      partUpdated("m-u2", ses, textPart("q2")),
      msgUpdated("m-a2", "assistant", ses),
      partUpdated("m-a2", ses, textPart("a2")),
      idle(ses),
      disposed(),
    ])

    const dir = join(LOG_BASE, ses)
    const turnFiles = filesIn(dir).filter((f) => /^00\d-2026/.test(f))
    expect(turnFiles.length).toBe(2)
    expect(turnFiles[0]).toMatch(/^001-\d{4}-/)
    expect(turnFiles[1]).toMatch(/^002-\d{4}-/)

    const lines = readJSONL(LOG_BASE, ses)
    expect(lines.some((l) => l.type === "session.compacted")).toBe(true)
  })
})
