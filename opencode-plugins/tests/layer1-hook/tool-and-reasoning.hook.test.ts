import { describe, expect, test } from "bun:test"
import { useTempCwd, makePlugin, drive, LOG_BASE, filesIn, yamlDocs, readJSONL } from "../helpers/harness"
import {
  sessionCreated, msgUpdated, partUpdated, idle, reasoningPart, textPart,
  toolCallPart, toolResultPart, toolInStatePart, stepFinish, disposed,
} from "../helpers/fixtures"
import { join } from "node:path"

describe("LG-HK-030 tool and reasoning", () => {
  useTempCwd()

  test("LG-HK-031 reasoning + text produce a step with thinking and response", async () => {
    const ses = "ses_test_tool_004"
    const p = await makePlugin()

    await drive(p, [
      sessionCreated(ses),
      msgUpdated("m-u", "user", ses),
      partUpdated("m-u", ses, textPart("q")),
      msgUpdated("m-a", "assistant", ses),
      partUpdated("m-a", ses, reasoningPart("let me think")),
      partUpdated("m-a", ses, textPart("answer")),
      idle(ses),
      disposed(),
    ])

    const dir = join(LOG_BASE, ses)
    const turnFile = filesIn(dir).find((f) => /^001-\d{4}/.test(f))!
    const doc = yamlDocs(join(dir, turnFile))[0]
    expect(doc.assistant[0].response).toContain("answer")
    const lines = readJSONL(LOG_BASE, ses)
    expect(lines.some((l) => l.partType === "reasoning" && l.reasoning)).toBe(true)
  })

  test("LG-HK-032 pending tool_call then tool_result yields one toolCall entry", async () => {
    const ses = "ses_test_tool_005"
    const p = await makePlugin()

    await drive(p, [
      sessionCreated(ses),
      msgUpdated("m-u", "user", ses),
      partUpdated("m-u", ses, textPart("run bash")),
      msgUpdated("m-a", "assistant", ses),
      partUpdated("m-a", ses, toolCallPart("call-1", "bash", "echo hi")),
      partUpdated("m-a", ses, toolResultPart("call-1", "hi\n")),
      partUpdated("m-a", ses, textPart("done")),
      idle(ses),
      disposed(),
    ])

    const dir = join(LOG_BASE, ses)
    const turnFile = filesIn(dir).find((f) => /^001-\d{4}/.test(f))!
    const doc = yamlDocs(join(dir, turnFile))[0]
    const step = doc.assistant[0]
    expect(step.tool_calls).toHaveLength(1)
    expect(step.tool_calls[0].tool).toBe("bash")
    expect(step.tool_calls[0].result).toBe("hi\n")
  })

  test("LG-HK-033 tool with inline state output (type 'tool') parses JSON results", async () => {
    const ses = "ses_test_tool_006"
    const p = await makePlugin()

    await drive(p, [
      sessionCreated(ses),
      msgUpdated("m-u", "user", ses),
      partUpdated("m-u", ses, textPart("json plz")),
      msgUpdated("m-a", "assistant", ses),
      partUpdated("m-a", ses, toolInStatePart("call-2", "read", "", JSON.stringify({ ok: true, n: 42 }))),
      partUpdated("m-a", ses, stepFinish()),
      idle(ses),
      disposed(),
    ])

    const dir = join(LOG_BASE, ses)
    const turnFile = filesIn(dir).find((f) => /^001-\d{4}/.test(f))!
    const doc = yamlDocs(join(dir, turnFile))[0]
    const step = doc.assistant[0]
    expect(JSON.parse(step.tool_calls[0].result as string)).toEqual({ ok: true, n: 42 })
  })
})
