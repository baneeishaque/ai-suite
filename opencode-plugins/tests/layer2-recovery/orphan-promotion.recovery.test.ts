import { describe, expect, test } from "bun:test"
import { useTempCwd, seedSession, resumeChild, tmpDir, LOG_BASE, filesIn, yamlDocs, readTurnsJSONL } from "../helpers/harness"
import { join } from "node:path"

describe("LG-RC-001 orphan promotion (resume subprocess)", () => {
  useTempCwd()

  test("LG-RC-002 orphan pending file is promoted to completed on subprocess resume", async () => {
    const ses = "ses_test_orphan_020"
    seedSession(ses, {
      "001-pending-2026-08-02T21-52-05-760Z.yaml":
        "---\nuser:\n  text: stale orphan turn\nassistant:\n  - response: interrupted\n",
    })

    resumeChild(tmpDir, ses)

    const dir = join(LOG_BASE, ses)
    const after = filesIn(dir)
    expect(after.filter((f) => f.includes("pending"))).toEqual([])
    expect(after.filter((f) => /^001-\d{4}/.test(f)).length).toBe(1)
    const doc = yamlDocs(join(dir, after.find((f) => /^001-\d{4}/.test(f))!))[0]
    expect(doc.user.text).toBe("stale orphan turn")
  })
})
