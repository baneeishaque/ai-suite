import { describe, expect, test } from "bun:test"
import { useTempCwd, seedSession, resumeChild, tmpDir, LOG_BASE, filesIn, yamlDocs } from "../helpers/harness"
import { join } from "node:path"

describe("LG-RC-010 orphan negative", () => {
  useTempCwd()

  test("LG-RC-011 resume does not corrupt a clean completed-only history", async () => {
    const ses = "ses_test_clean_021"
    seedSession(ses, {
      "001-2026-08-02T21-52-05-760Z.yaml":
        "---\nuser:\n  text: first turn\nassistant:\n  - response: first answer\n",
    })

    resumeChild(tmpDir, ses)

    const dir = join(LOG_BASE, ses)
    const after = filesIn(dir)
    expect(after.filter((f) => f.includes("pending"))).toEqual([])
    expect(after.filter((f) => /^00\d-2026/.test(f))).toEqual(["001-2026-08-02T21-52-05-760Z.yaml"])
    const doc = yamlDocs(join(dir, "001-2026-08-02T21-52-05-760Z.yaml"))[0]
    expect(doc.user.text).toBe("first turn")
  })
})
