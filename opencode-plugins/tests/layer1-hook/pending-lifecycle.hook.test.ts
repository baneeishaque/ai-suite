import { describe, expect, test } from "bun:test"
import { useTempCwd, makePlugin, drive, LOG_BASE, filesIn } from "../helpers/harness"
import { sessionCreated, msgUpdated, partUpdated, textPart, idle, stepFinish, disposed } from "../helpers/fixtures"
import { join } from "node:path"

describe("LG-HK-020 pending lifecycle", () => {
  useTempCwd()

  test("LG-HK-021 pending file exists after step-finish and is replaced on idle", async () => {
    const ses = "ses_test_pending_003"
    const p = await makePlugin()

    await drive(p, [
      sessionCreated(ses),
      msgUpdated("m-user-1", "user", ses),
      partUpdated("m-user-1", ses, textPart("q")),
      msgUpdated("m-assistant-1", "assistant", ses),
      partUpdated("m-assistant-1", ses, textPart("a")),
      partUpdated("m-assistant-1", ses, stepFinish()),
    ])

    const dir = join(LOG_BASE, ses)
    const pendingFiles = filesIn(dir).filter((f) => f.includes("pending"))
    expect(pendingFiles.length).toBe(1)
    expect(pendingFiles[0]).toMatch(/^001-pending-/)

    await drive(p, [idle(ses), disposed()])

    const after = filesIn(dir)
    expect(after.filter((f) => f.includes("pending"))).toEqual([])
    expect(after.filter((f) => /^00\d-2026/.test(f)).length).toBe(1)
  })
})
