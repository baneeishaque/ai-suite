import type { Plugin } from "@opencode-ai/plugin"
import { mkdirSync, appendFileSync, writeFileSync, existsSync, readFileSync } from "node:fs"
import { join } from "node:path"
import { dump, loadAll } from "js-yaml"

const LOG_BASE = ".opencode/logs"

function ts(): string {
  return new Date().toISOString()
}

function j(o: unknown): string {
  try { return JSON.stringify(o) } catch { return JSON.stringify({ error: "serialize failed" }) }
}

// ---------------------------------------------------------------------------
// Time helpers
// ---------------------------------------------------------------------------

function formatLocal(iso: string | null): string {
  if (!iso) return ""
  const d = new Date(iso)
  const m = `${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear()}`
  const h = d.getHours() % 12 || 12
  const ap = d.getHours() >= 12 ? "PM" : "AM"
  const t = `${h}:${String(d.getMinutes()).padStart(2, "0")}:${String(d.getSeconds()).padStart(2, "0")}.${String(d.getMilliseconds()).padStart(3, "0")}`
  const tz = new Intl.DateTimeFormat("en-US", { timeZoneName: "short" }).format(d).split(", ").pop() ?? ""
  return `${m}, ${t} ${ap} ${tz}`
}

function formatDuration(ms: number): string {
  if (ms >= 1000) return (ms / 1000).toFixed(3) + "s"
  return ms + "ms"
}

// ---------------------------------------------------------------------------
// YAML builder (js-yaml)
// ---------------------------------------------------------------------------

function buildYAML(docs: Record<string, unknown>[]): string {
  if (docs.length === 0) return ""
  return docs.map((d) => "---\n" + dump(d, { indent: 2, lineWidth: -1, noRefs: true, quotingType: '"', noCompatMode: true }) + "\n").join("")
}

// ---------------------------------------------------------------------------
// JSONL
// ---------------------------------------------------------------------------

function writeJSONL(sid: string, entry: Record<string, unknown>) {
  try {
    mkdirSync(LOG_BASE, { recursive: true })
    appendFileSync(join(LOG_BASE, `${sid}.jsonl`), j(entry) + "\n")
  } catch { /* no crash */ }
}

function parseTaskResult(result: string): { sessionId: string | null; state: string | null; taskResult: string | null } | null {
  const idMatch = result.match(/<task\s+id="([^"]+)"/)
  const stateMatch = result.match(/state="([^"]+)"/)
  const resultMatch = result.match(/<task_result>([\s\S]*?)<\/task_result>/)
  if (!idMatch && !stateMatch && !resultMatch) return null
  return {
    sessionId: idMatch ? idMatch[1] : null,
    state: stateMatch ? stateMatch[1] : null,
    taskResult: resultMatch ? resultMatch[1].trim() : result,
  }
}

function normalizeResult(result: string): string {
  if (!result) return result
  try {
    const parsed = JSON.parse(result)
    if (typeof parsed === "object" && parsed !== null) {
      return JSON.stringify(parsed, null, 2)
    }
  } catch { /* not JSON — return as-is */ }
  return result
}

function writeYAML(ses: string, includePending = false) {
  try {
    const s = getSS(ses)
    const yp = join(LOG_BASE, `${ses}.yaml`)
    const header: Record<string, unknown> = {
      session: { id: ses, created: formatLocal(s.created ?? ts()), updated: formatLocal(s.updated ?? ts()) },
    }
    if (s.model) header.model = s.model
    if (s.title) header.title = s.title
    if (s.compactedAt) {
      header.session = { ...header.session as Record<string, unknown>, compacted: formatLocal(s.compactedAt) }
    }
    const docs: Record<string, unknown>[] = [header, ...s.turns]
    if (includePending && s.turn && s.turn.steps.length > 0) {
      docs.push(s.turn.toFields())
    }
    writeFileSync(yp, buildYAML(docs))
  } catch { /* no crash */ }
}

function finalizeTurn(ses: string) {
  const s = getSS(ses)
  if (!s.turn || s.turn.steps.length === 0) return false
  s.turn.endTime = ts()
  if (s.turn.currentStep && !s.turn.currentStep.endTime) {
    s.turn.currentStep.endTime = ts()
    if (s.turn.currentStep.thinkingStartTime != null && s.turn.currentStep.thinkingDuration == null) {
      s.turn.currentStep.thinkingDuration = Date.now() - new Date(s.turn.currentStep.thinkingStartTime).getTime()
    }
  }
  pushTurn(s.turn.toFields(), ses)
  s.turn = null
  return true
}

function pushTurn(turnFields: Record<string, unknown>, ses: string) {
  const s = getSS(ses)
  s.turns.push(turnFields)
  if (s.turnsFile) {
    try {
      mkdirSync(LOG_BASE, { recursive: true })
      appendFileSync(s.turnsFile, j(turnFields) + "\n")
    } catch { /* no crash */ }
  }
}

function stateFile(sid: string): string {
  return join(LOG_BASE, `${sid}.state.json`)
}

function loadState(sid: string): Record<string, unknown> {
  try { return JSON.parse(readFileSync(stateFile(sid), "utf-8")) } catch { return {} }
}

function saveState(sid: string, data: Record<string, unknown>) {
  try { mkdirSync(LOG_BASE, { recursive: true }); writeFileSync(stateFile(sid), j(data)) } catch { /* no crash */ }
}

function initSession(ses: string, info?: Record<string, unknown>) {
  sid = ses
  const s = getSS(ses)
  s.turnsFile = join(LOG_BASE, `${ses}.turns.jsonl`)
  s.turns = []
  if (existsSync(s.turnsFile)) {
    for (const line of readFileSync(s.turnsFile, "utf-8").trim().split("\n").filter(Boolean)) {
      try { s.turns.push(JSON.parse(line) as Record<string, unknown>) } catch { /* skip bad line */ }
    }
  }
  const yp = join(LOG_BASE, `${ses}.yaml`)
  if (existsSync(yp) && s.turns.length === 0) {
    try {
      const existing = loadAll(readFileSync(yp, "utf-8")) as Record<string, unknown>[]
      for (let i = 1; i < existing.length; i++) {
        const d = existing[i]
        if (d?.user) s.turns.push(d)
      }
    } catch { /* skip bad yaml recovery */ }
  }
  s.created = (loadState(ses).created as string) ?? (info?.time?.created ? new Date((info.time as Record<string, unknown>).created as string).toISOString() : ts())
  s.updated = info?.time?.updated ? new Date((info.time as Record<string, unknown>).updated as string).toISOString() : ts()
  s.model = modelFromInfo(info ?? {})
  s.title = info?.title as string ?? null
  s.turn = null
  s.compactedAt = null
  s.firstUserTime = null
}

// ---------------------------------------------------------------------------
// Turn model
// ---------------------------------------------------------------------------

interface ModelInfo {
  id: string; provider: string
}

interface ToolCall {
  tool: string; args: unknown; result: unknown
}

class Step {
  model: ModelInfo | null = null
  agent: string | null = null
  thinking: string[] = []
  thinkingStartTime: string | null = null
  thinkingDuration: number | null = null
  responseText: string[] = []
  toolCalls: ToolCall[] = []
  startTime = ts()
  endTime: string | null = null
  pendingTool: string | null = null
  pendingArgs: unknown = null

  get hasContent(): boolean {
    return this.thinking.length > 0 || this.toolCalls.length > 0 || this.responseText.length > 0
  }

  toFields(): Record<string, unknown> {
    const a: Record<string, unknown> = {}
    if (this.agent) a.agent = this.agent
    if (this.model) a.model = { id: this.model.id, provider: this.model.provider }
    if (this.thinking.length > 0) {
      const text = this.thinking.filter(Boolean).join("\n")
      if (text) a.thinking = text
    }
    if (this.thinkingDuration != null) {
      a.thinking_duration = formatDuration(this.thinkingDuration)
      a.thinking_duration_ms = this.thinkingDuration
    }
    if (this.toolCalls.length > 0) {
      a.tool_calls = this.toolCalls.map((tc) => {
        const base: Record<string, unknown> = { tool: tc.tool, args: tc.args }
        if (tc.tool === "task" && typeof tc.result === "object" && tc.result !== null) {
          const r = tc.result as Record<string, unknown>
          if (r.sessionId) base.task_session_id = r.sessionId
          if (r.state) base.task_state = r.state
          if (r.taskResult) base.task_result = r.taskResult
        } else {
          base.result = tc.result
        }
        return base
      })
    }
    if (this.startTime) a.time = formatLocal(this.startTime)
    if (this.responseText.length > 0) a.response = this.responseText.join("")
    if (this.startTime && this.endTime) {
      const ms = new Date(this.endTime).getTime() - new Date(this.startTime).getTime()
      a.duration = formatDuration(ms)
      a.duration_ms = ms
    }
    return a
  }
}

class Turn {
  userText = ""
  userTime: string | null = null
  startTime = ts()
  endTime: string | null = null
  userMessageID: string | null = null
  steps: Step[] = []
  currentStep: Step | null = null

  toFields(): Record<string, unknown> {
    const userField: Record<string, unknown> = { text: this.userText }
    if (this.userTime) userField.time = formatLocal(this.userTime)
    const out: Record<string, unknown> = { user: userField }
    const stepFields = this.steps.filter((s) => s.hasContent).map((s) => s.toFields())
    if (stepFields.length > 0) {
      out.assistant = stepFields
    }
    return out
  }
}

function modelFromInfo(info: Record<string, unknown>): ModelInfo | null {
  // AssistantMessage: flat modelID / providerID
  if (info.modelID) return { id: info.modelID as string, provider: (info.providerID as string) ?? "" }
  // UserMessage: nested model { providerID, modelID }
  if (info.model && typeof info.model === "object") {
    const m = info.model as Record<string, unknown>
    if (m.modelID) return { id: m.modelID as string, provider: (m.providerID as string) ?? "" }
  }
  return null
}

// ---------------------------------------------------------------------------
// Per-session state
// ---------------------------------------------------------------------------

interface SessionState {
  turn: Turn | null
  turns: Record<string, unknown>[]
  turnsFile: string | null
  model: ModelInfo | null
  title: string | null
  compactedAt: string | null
  firstUserTime: string | null
  created: string | null
  updated: string | null
}
const SS = new Map<string, SessionState>()

function getSS(ses: string): SessionState {
  let s = SS.get(ses)
  if (!s) {
    s = { turn: null, turns: [], turnsFile: null, model: null, title: null, compactedAt: null, firstUserTime: null, created: null, updated: null }
    SS.set(ses, s)
  }
  return s
}

let sid: string | null = null

interface MsgInfo {
  role: string; sessionID: string | null; model: ModelInfo | null; agent: string | null; userTime: string | null
}
const msgStore = new Map<string, MsgInfo>()

// ---------------------------------------------------------------------------
// Plugin
// ---------------------------------------------------------------------------

export const OpenCodeLogger: Plugin = async () => {
  return {
    event: async ({ event }) => {
      try {
        const p = (event as any).properties
        const now = ts()

        switch (event.type) {
            case "session.created": {
              const info = p?.info
              if (!info?.id) break
              if (sid) {
                // Sub-agent session — don't overwrite main session state
                writeJSONL(sid, { timestamp: now, sessionID: info.id, type: "session.sub_created" })
                break
              }
              initSession(info.id as string, info)
              const s = getSS(info.id as string)
              msgStore.clear()
              saveState(sid!, { created: s.created })
              writeJSONL(sid!, { timestamp: now, sessionID: sid, type: "session.created", model: s.model, title: s.title })
              break
            }

           case "session.updated": {
             const info = p?.info
             if (!info?.id || info.id !== sid) break
             const s = getSS(info.id as string)
             if (info.title) s.title = info.title
             if (info.time?.updated) s.updated = new Date(info.time.updated).toISOString()
             break
           }

           case "message.updated": {
             const info = p?.info
             if (!info?.id) break
             const msgModel = modelFromInfo(info)
             msgStore.set(info.id, {
               role: info.role,
               sessionID: info.sessionID ?? null,
               model: msgModel,
               agent: info.role === "user" ? (info.agent ?? null) : null,
               userTime: info.time?.created ? new Date(info.time.created).toISOString() : null,
             })
             if (info.role === "assistant") {
               const ses = info.sessionID ?? sid
               if (ses) {
                 const s = getSS(ses as string)
                 if (s.turn) {
                   if (s.turn.currentStep) {
                     s.turn.currentStep.endTime = ts()
                     if (s.turn.currentStep.thinkingStartTime != null && s.turn.currentStep.thinkingDuration == null) {
                       s.turn.currentStep.thinkingDuration = Date.now() - new Date(s.turn.currentStep.thinkingStartTime).getTime()
                     }
                   }
                   if (msgModel) s.model = msgModel
                   const step = new Step()
                   step.model = msgModel ?? s.model
                   step.agent = info.agent ?? null
                   step.startTime = ts()
                   s.turn.steps.push(step)
                   s.turn.currentStep = step
                 }
               }
             }
             break
           }

           case "message.part.updated": {
              const part = p?.part
              if (!part?.messageID) break
              const mi = msgStore.get(part.messageID)
              const role = mi?.role ?? "unknown"
              const ses = mi?.sessionID ?? sid
              if (!ses) break
              // Lazy init: resumed sessions may not fire session.created
              if (!sid) initSession(ses as string)

              const s = getSS(ses as string)
              if (role === "user" && part.type === "text" && (!s.turn || s.turn.userMessageID !== part.messageID)) {
                if (mi?.userTime && s.firstUserTime == null) s.firstUserTime = mi.userTime
                if (s.turn && s.turn.steps.length > 0) {
                  s.turn.endTime = ts()
                  if (s.turn.currentStep && !s.turn.currentStep.endTime) {
                    s.turn.currentStep.endTime = ts()
                    if (s.turn.currentStep.thinkingStartTime != null && s.turn.currentStep.thinkingDuration == null) {
                      s.turn.currentStep.thinkingDuration = Date.now() - new Date(s.turn.currentStep.thinkingStartTime).getTime()
                    }
                  }
                  pushTurn(s.turn.toFields(), ses as string)
                  s.updated = ts()
                  if (s.firstUserTime && s.created && new Date(s.firstUserTime).getTime() < new Date(s.created).getTime()) {
                    s.created = s.firstUserTime
                  }
                  writeJSONL(ses as string, { timestamp: ts(), sessionID: ses, type: "turn.complete", turnIndex: s.turns.length - 1 })
                  writeYAML(ses as string)
                }
                s.turn = new Turn()
                s.turn.userText = part.text ?? ""
                s.turn.userTime = mi?.userTime ?? null
                s.turn.userMessageID = part.messageID
                s.turn.startTime = ts()
              }

              const stp = s.turn ? (s.turn.currentStep ?? (() => {
                const ns = new Step()
                ns.model = s.model
                s.turn!.steps.push(ns)
                s.turn!.currentStep = ns
                return ns
              })()) : null

              const entry: Record<string, unknown> = {
                timestamp: ts(), sessionID: ses, type: "message.part", role,
                partType: part.type, messageID: part.messageID,
                agent: mi?.agent ?? null,
              }
              if (s.model) { entry.modelID = s.model.id; entry.providerID = s.model.provider }

            switch (part.type) {
              case "text":
                entry.text = part.text ?? ""
                if (stp && role === "assistant") {
                  stp.responseText.push(part.text ?? "")
                  if (stp.thinkingStartTime != null && stp.thinkingDuration == null) {
                    const end = ts()
                    stp.thinkingDuration = new Date(end).getTime() - new Date(stp.thinkingStartTime).getTime()
                  }
                }
                break
              case "reasoning":
                entry.reasoning = part.text ?? part.reasoning ?? ""
                if (stp && role === "assistant") {
                  stp.thinking.push(part.text ?? part.reasoning ?? "")
                  if (stp.thinkingStartTime == null) stp.thinkingStartTime = ts()
                }
                break
              case "tool_call":
              case "tool":
                entry.toolID = part.callID ?? ""
                entry.toolName = part.tool ?? ""
                entry.args = part.state?.input ?? ""
                entry.result = normalizeResult(part.state?.output ?? part.state?.error ?? "")
                entry.status = part.state?.status ?? ""
                if (stp && part.tool) {
                  if (entry.result) {
                    const rawResult = normalizeResult(entry.result as string)
                    const isTask = (stp.pendingTool ?? part.tool) === "task"
                    stp.toolCalls.push({
                      tool: stp.pendingTool ?? part.tool,
                      args: stp.pendingArgs ?? (part.state?.input ?? ""),
                      result: isTask ? (parseTaskResult(rawResult) ?? rawResult) : rawResult,
                    })
                    stp.pendingTool = null; stp.pendingArgs = null
                  } else {
                    // First arrival of this tool — compute thinking duration if reasoning just ended
                    if (stp.thinkingStartTime != null && stp.thinkingDuration == null) {
                      stp.thinkingDuration = Date.now() - new Date(stp.thinkingStartTime).getTime()
                    }
                    stp.pendingTool = part.tool; stp.pendingArgs = part.state?.input ?? ""
                  }
                }
                break
               case "tool_result":
                  entry.toolCallID = part.toolCallID ?? ""
                  entry.result = normalizeResult(part.data ?? part.text ?? "")
                  if (stp && stp.pendingTool) {
                    stp.toolCalls.push({
                      tool: stp.pendingTool, args: stp.pendingArgs ?? "",
                      result: normalizeResult(part.data ?? part.text ?? ""),
                    })
                    stp.pendingTool = null; stp.pendingArgs = null
                 }
                 break
               case "step-finish":
                 writeYAML(ses, true)
                 break
              default:
                entry.text = part.text ?? ""
            }

            writeJSONL(ses, entry)
            break
          }

            case "session.status": {
              const props = p?.properties ?? p
              if (props?.status?.type !== "idle") break
              const ses = props?.sessionID ?? sid
              if (!ses || ses !== sid) break

              const s = getSS(ses)
              if (finalizeTurn(ses)) {
                if (s.firstUserTime && s.created && new Date(s.firstUserTime).getTime() < new Date(s.created).getTime()) {
                  s.created = s.firstUserTime
                }
                writeJSONL(ses, { timestamp: ts(), sessionID: ses, type: "turn.complete", turnIndex: s.turns.length - 1 })
              }
              s.updated = ts()
              writeYAML(ses)
              break
            }

           case "session.compacted": {
              const ses = p?.sessionID ?? sid
              if (!ses || ses !== sid) break
              const s = getSS(ses)
              s.compactedAt = ts()
              writeJSONL(ses, { timestamp: ts(), sessionID: ses, type: "session.compacted" })
              break
            }

            case "session.deleted":
            case "server.instance.disposed": {
              const info = p?.info
              const ses = event.type === "session.deleted" ? (info?.id ?? sid) : sid
              if (!ses || ses !== sid) break
              const s = getSS(ses)
              s.updated = ts()
              if (finalizeTurn(ses)) {
                writeJSONL(ses, { timestamp: ts(), sessionID: ses, type: "turn.complete", turnIndex: s.turns.length - 1 })
              }
              writeYAML(ses)
              writeJSONL(ses, {
                timestamp: ts(), sessionID: ses,
                type: event.type === "session.deleted" ? "session.deleted" : "server.shutdown",
              })
              if (sid === ses) sid = null
              break
            }
        }
      } catch { /* no crash */ }
    },
  }
}
