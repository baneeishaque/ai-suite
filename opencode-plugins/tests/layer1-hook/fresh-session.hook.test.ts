import { describe, expect, test } from "bun:test"
import { useTempCwd, makePlugin, drive, LOG_BASE, filesIn, yamlDocs, readJSONL, readTurnsJSONL } from "../helpers/harness"
import { sessionCreated, msgUpdated, partUpdated, textPart, idle, disposed, MARKERS } from "../helpers/fixtures"
import { join } from "node:path"

describe("LG-HK-001 fresh session", () => {
  useTempCwd()

  test("LG-HK-002 single user turn produces header, completed turn, jsonl and turns.jsonl", async () => {
    const ses = "ses_test_fresh_001"
    const p = await makePlugin()

    await drive(p, [
      sessionCreated(ses, { modelID: "m-test", providerID: "opencode" }),
      msgUpdated("m-user-1", "user", ses),
      partUpdated("m-user-1", ses, textPart(MARKERS.userText)),
      msgUpdated("m-assistant-1", "assistant", ses),
      partUpdated("m-assistant-1", ses, textPart(MARKERS.assistantText)),
      idle(ses),
      disposed(),
    ])

    const dir = join(LOG_BASE, ses)
    const files = filesIn(dir)
        expect(files.some((f) => /^000-header-\d{4}/.test(f))).toBe(true)
    const turnFiles = files.filter((f) => /^001-/.test(f))
    expect(turnFiles.length).toBe(1)
    expect(turnFiles[0]).toMatch(/^001-\d{4}-/)

    const doc = yamlDocs(join(dir, turnFiles[0]))[0]
    expect(doc.user.text).toBe(MARKERS.userText)
    expect(doc.assistant).toBeDefined()

    const lines = readJSONL(LOG_BASE, ses)
    const types = lines.map((l) => l.type)
    expect(types).toContain("session.created")
    expect(types).toContain("message.part")
    expect(types).toContain("turn.complete")
    const created = lines.find((l) => l.type === "session.created")
    expect(created.title).toBe("test")
    const completed = lines.find((l) => l.type === "turn.complete")
    expect(completed.turnIndex).toBe(0)

    const turns = readTurnsJSONL(LOG_BASE, ses)
    expect(turns.length).toBe(1)
    expect(turns[0].user.text).toContain(MARKERS.userText)
  })
})
