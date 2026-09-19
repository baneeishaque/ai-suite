import { describe, expect, test } from "bun:test"
import { useTempCwd, makePlugin, drive, LOG_BASE, filesIn, readJSONL } from "../helpers/harness"
import { sessionCreated, msgUpdated, partUpdated, textPart, idle, stepFinish, disposed } from "../helpers/fixtures"
import { join } from "node:path"

describe("LG-HK-040 sub-agent", () => {
  useTempCwd()

  test("LG-HK-041 session.created while sid active is logged as session.sub_created", async () => {
    const main = "ses_test_main_007"
    const sub = "ses_test_sub_008"
    const p = await makePlugin()

    await drive(p, [
      sessionCreated(main),
      sessionCreated(sub),
      disposed(),
    ])

    const mainLines = readJSONL(LOG_BASE, main)
    const subCreated = mainLines.filter((l) => l.type === "session.sub_created")
    expect(subCreated.length).toBe(1)
  })

  test("LG-HK-042 sub-agent parts write to the sub session dir; idle for sub is ignored", async () => {
    const main = "ses_test_main_009"
    const sub = "ses_test_sub_010"
    const p = await makePlugin()

    await drive(p, [
      sessionCreated(main),
      sessionCreated(sub),
      msgUpdated("m-su", "user", sub),
      partUpdated("m-su", sub, textPart("sub question")),
      msgUpdated("m-sa", "assistant", sub),
      partUpdated("m-sa", sub, textPart("sub answer")),
      partUpdated("m-sa", sub, stepFinish()),
      idle(sub),
      disposed(),
    ])

    const subDir = join(LOG_BASE, sub)
    expect(filesIn(subDir).some((f) => f.startsWith("000-header-"))).toBe(true)
    expect(filesIn(subDir).some((f) => f.includes("pending"))).toBe(true)

    const subLines = readJSONL(LOG_BASE, sub)
    expect(subLines.some((l) => l.type === "turn.complete")).toBe(false)
  })
})
