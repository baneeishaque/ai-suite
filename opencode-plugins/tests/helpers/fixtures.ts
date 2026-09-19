import { randomUUID } from "node:crypto"

export interface HookEvent {
  id: string
  type: string
  properties: Record<string, unknown>
}

export const MARKERS = {
  userText: "Hello logger",
  assistantText: "Hi from the assistant",
  e2ePrompt: "Reply with exactly: E2E-LOGGER-OK",
}

export function ev(type: string, properties: Record<string, unknown>): HookEvent {
  return { id: randomUUID(), type, properties }
}

export interface SessionOpts {
  title?: string
  modelID?: string
  providerID?: string
  model?: { id: string; provider: string }
}

export function sessionCreated(ses: string, opts: SessionOpts = {}) {
  return ev("session.created", {
    info: {
      id: ses,
      title: opts.title ?? "test",
      time: { created: new Date().toISOString(), updated: new Date().toISOString() },
      modelID: opts.modelID,
      providerID: opts.providerID,
      model: opts.model,
    },
  })
}

export function sessionUpdated(ses: string, title: string) {
  return ev("session.updated", {
    info: { id: ses, title, time: { updated: new Date().toISOString() } },
  })
}

export function msgUpdated(
  msgID: string,
  role: "user" | "assistant",
  ses: string,
  opts: { agent?: string; modelID?: string; providerID?: string } = {},
) {
  return ev("message.updated", {
    info: {
      id: msgID,
      role,
      sessionID: ses,
      time: { created: new Date().toISOString() },
      agent: opts.agent,
      modelID: opts.modelID,
      providerID: opts.providerID,
    },
  })
}

export function partUpdated(msgID: string, ses: string, part: Record<string, unknown>) {
  return ev("message.part.updated", { part: { messageID: msgID, sessionID: ses, ...part } })
}

export const textPart = (t: string) => ({ type: "text", text: t })
export const reasoningPart = (t: string) => ({ type: "reasoning", text: t })
export const toolCallPart = (callID: string, tool: string, input: string, status = "pending") => ({
  type: "tool_call",
  callID,
  tool,
  state: { input, status },
})
export const toolResultPart = (callID: string, output: string) => ({
  type: "tool_result",
  toolCallID: callID,
  data: output,
})
export const toolInStatePart = (callID: string, tool: string, input: string, output: string, status = "completed") => ({
  type: "tool",
  callID,
  tool,
  state: { input, output, status },
})
export const stepFinish = () => ({ type: "step-finish" })

export function idle(ses: string) {
  return ev("session.status", { sessionID: ses, status: { type: "idle" } })
}

export function compacted(ses: string) {
  return ev("session.compacted", { sessionID: ses })
}

export function deleted(ses: string) {
  return ev("session.deleted", { info: { id: ses } })
}

export function disposed() {
  return ev("server.instance.disposed", {})
}
