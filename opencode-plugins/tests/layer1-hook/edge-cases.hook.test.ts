import { describe, expect, test } from "bun:test"
import { useTempCwd, makePlugin, drive, LOG_BASE, filesIn, readJSONL, yamlDocs } from "../helpers/harness"
import { sessionCreated, msgUpdated, partUpdated, textPart, idle, deleted, disposed } from "../helpers/fixtures"
import { join } from "node:path"

describe("LG-HK-060 edge cases", () => {
  useTempCwd()

  test("LG-HK-061 unknown event types are ignored without crash", async () => {
    const ses = "ses_test_edge_012"
    const p = await makePlugin()
    await drive(p, [
      sessionCreated(ses),
      { id: "x1", type: "some.future.event", properties: { anything: 1 } },
      idle(ses),
      disposed(),
    ])
    expect(filesIn(join(LOG_BASE, ses)).some((f) => f.startsWith("000-header-"))).toBe(true)
  })

  test("LG-HK-062 part before session.created lazy-inits without crash", async () => {
    const ses = "ses_test_edge_013"
    const p = await makePlugin()
    await drive(p, [
      msgUpdated("m-u", "user", ses),
      partUpdated("m-u", ses, textPart("orphan part")),
      disposed(),
    ])
    expect(readJSONL(LOG_BASE, ses).length).toBeGreaterThan(0)
  })

  test("LG-HK-063 duplicate session.created for same id is treated as sub-agent", async () => {
    const ses = "ses_test_edge_014"
    const p = await makePlugin()
    await drive(p, [sessionCreated(ses), sessionCreated(ses), disposed()])
    const lines = readJSONL(LOG_BASE, ses)
    expect(lines.filter((l) => l.type === "session.sub_created").length).toBe(1)
  })

  test("LG-HK-064 session.deleted finalizes, then a new session.created is fresh again", async () => {
    const ses1 = "ses_test_edge_015"
    const ses2 = "ses_test_edge_016"
    const p = await makePlugin()
    await drive(p, [
      sessionCreated(ses1),
      msgUpdated("m-u1", "user", ses1),
      partUpdated("m-u1", ses1, textPart("q1")),
      msgUpdated("m-a1", "assistant", ses1),
      partUpdated("m-a1", ses1, textPart("a1")),
      deleted(ses1),
      sessionCreated(ses2),
      disposed(),
    ])
    const d1 = join(LOG_BASE, ses1)
    expect(readJSONL(LOG_BASE, ses1).some((l) => l.type === "session.deleted")).toBe(true)
    const d2 = join(LOG_BASE, ses2)
    expect(readJSONL(LOG_BASE, ses2).some((l) => l.type === "session.sub_created")).toBe(false)
  })

  test("LG-HK-065 server.instance.disposed writes shutdown marker and clears sid", async () => {
    const ses = "ses_test_edge_017"
    const p = await makePlugin()
    await drive(p, [sessionCreated(ses), msgUpdated("m-u", "user", ses), partUpdated("m-u", ses, textPart("q")), disposed(), sessionCreated("ses_test_edge_018"), disposed()])
    const lines = readJSONL(LOG_BASE, ses)
    expect(lines.some((l) => l.type === "server.shutdown")).toBe(true)
    await drive(p, [sessionCreated("ses_test_edge_018")])
    expect(readJSONL(LOG_BASE, "ses_test_edge_018").some((l) => l.type === "session.sub_created")).toBe(false)
  })

  test("LG-HK-066 user turn with empty assistant content completes cleanly", async () => {
    const ses = "ses_test_edge_019"
    const p = await makePlugin()
    await drive(p, [sessionCreated(ses), msgUpdated("m-u", "user", ses), partUpdated("m-u", ses, textPart("q")), idle(ses), disposed()])
    const dir = join(LOG_BASE, ses)
    const turnFiles = filesIn(dir).filter((f) => /^001-\d{4}/.test(f))
    expect(turnFiles).toEqual([])
  })
})
