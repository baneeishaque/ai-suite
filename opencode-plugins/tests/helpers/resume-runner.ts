import { join } from "node:path"
import { randomUUID } from "node:crypto"

const dirIdx = process.argv.indexOf("--dir")
const sesIdx = process.argv.indexOf("--session")
if (dirIdx < 0 || sesIdx < 0) {
  console.error("usage: resume-runner --dir <cwd> --session <sesId>")
  process.exit(2)
}
const cwd = process.argv[dirIdx + 1]
const ses = process.argv[sesIdx + 1]
process.chdir(cwd)

const { OpenCodeLogger } = await import(join(import.meta.dir, "../../opencode-logger"))
const p = await OpenCodeLogger({} as never)
await p.event({
  event: {
    id: randomUUID(),
    type: "session.created",
    properties: {
      info: { id: ses, title: "resumed", time: { created: new Date().toISOString(), updated: new Date().toISOString() } },
    },
  },
})
console.log("resumed", ses)
