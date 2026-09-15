// Copilot hook payload factories.
// Shapes match the VS Code agent-hooks contract (session_id,
// hook_event_name, ISO timestamp, cwd, per-event snake_case fields).
export const MARKERS = {
  userText: "Hello copilot logger",
  toolResponse: "File contents here",
};

let seq = 0;

export function base(sessionId, hook_event_name, extra = {}) {
  return {
    session_id: sessionId,
    hook_event_name,
    timestamp: new Date(Date.now() + seq++).toISOString(),
    cwd: "",
    ...extra,
  };
}

export const sessionStart = (sessionId, source = "new") => base(sessionId, "SessionStart", { source, model: "auto" });

export const userPrompt = (sessionId, prompt = MARKERS.userText) => base(sessionId, "UserPromptSubmit", { prompt });

export const preTool = (sessionId, tool = "copilot_readFile", input = { filePath: "src/a.ts" }, toolUseId = "tool-1") =>
  base(sessionId, "PreToolUse", { tool_name: tool, tool_input: input, tool_use_id: toolUseId });

export const postTool = (sessionId, tool = "copilot_readFile", input = { filePath: "src/a.ts" }, response = MARKERS.toolResponse, toolUseId = "tool-1") =>
  base(sessionId, "PostToolUse", { tool_name: tool, tool_input: input, tool_use_id: toolUseId, tool_response: response });

export const preCompact = (sessionId, trigger = "auto") => base(sessionId, "PreCompact", { trigger });

export const subagentStart = (sessionId, agentId = "subagent-1", agentType = "Plan") =>
  base(sessionId, "SubagentStart", { agent_id: agentId, agent_type: agentType });

export const subagentStop = (sessionId, agentId = "subagent-1") =>
  base(sessionId, "SubagentStop", { agent_id: agentId, stop_hook_active: false });

export const stop = (sessionId) => base(sessionId, "Stop", { stop_hook_active: false });

export const unknownEvent = (sessionId) => base(sessionId, "SomeFutureEvent", {});

// Live transcript JSONL stream (one envelope per line), ping-shaped.
export function pingStream(sessionId, userText = "Ping Test", assistantText = "Pong.") {
  const t = "2026-09-15T02:48:36.924Z";
  const lines = [
    { type: "session.start", data: { sessionId, version: 1, producer: "copilot-agent", copilotVersion: "0.66.2026091401", vscodeVersion: "1.138.0-insider", startTime: t }, id: "evt-1", timestamp: t, parentId: null },
    { type: "user.message", data: { content: userText, attachments: [] }, id: "evt-2", timestamp: t, parentId: "evt-1" },
    { type: "assistant.turn_start", data: { turnId: "0" }, id: "evt-3", timestamp: t, parentId: "evt-2" },
    { type: "assistant.message", data: { messageId: "msg-1", content: assistantText, toolRequests: [], reasoningText: "" }, id: "evt-4", timestamp: t, parentId: "evt-3" },
    { type: "assistant.turn_end", data: { turnId: "0" }, id: "evt-5", timestamp: t, parentId: "evt-4" },
  ];
  return lines.map((l) => JSON.stringify(l)).join("\n");
}

// Live stream with reasoning + a tool request (arguments as JSON string,
// exactly as the agent host writes them).
export function toolCallStream(sessionId) {
  const t = "2026-09-15T02:48:36.924Z";
  const lines = [
    { type: "session.start", data: { sessionId, version: 1, producer: "copilot-agent", copilotVersion: "0.66.2026091401", vscodeVersion: "1.138.0-insider", startTime: t }, id: "evt-1", timestamp: t, parentId: null },
    { type: "user.message", data: { content: "List files", attachments: [] }, id: "evt-2", timestamp: t, parentId: "evt-1" },
    { type: "assistant.turn_start", data: { turnId: "0" }, id: "evt-3", timestamp: t, parentId: "evt-2" },
    {
      type: "assistant.message",
      data: {
        messageId: "msg-2",
        content: "I'll list the directory.",
        toolRequests: [{ toolCallId: "toolu_1", name: "copilot_listDirectory", arguments: "{\"path\": \"src\"}" }],
        reasoningText: "Need the file list first.",
      },
      id: "evt-4", timestamp: t, parentId: "evt-3",
    },
    { type: "assistant.turn_end", data: { turnId: "0" }, id: "evt-5", timestamp: t, parentId: "evt-4" },
  ];
  return lines.map((l) => JSON.stringify(l)).join("\n");
}

// CLI-shaped live stream (session-state/events.jsonl): session context,
// model_change, interaction pairing, per-message model + output tokens,
// usage checkpoint. Mirrors the real Copilot CLI ping capture.
export function cliStream(sessionId, userText = "Ping Test", assistantText = "Pong.") {
  const t = "2026-09-15T09:33:31.094Z";
  const lines = [
    {
      type: "session.start",
      data: {
        sessionId, version: 1, producer: "copilot-agent", copilotVersion: "1.0.81-0", startTime: t,
        context: { cwd: "/tmp/ws", gitRoot: "/tmp/ws", repository: "acme/demo", hostType: "github", branch: "main" },
      },
      id: "evt-1", timestamp: t, parentId: null,
    },
    { type: "session.model_change", data: { newModel: "auto" }, id: "evt-2", timestamp: t, parentId: "evt-1" },
    {
      type: "user.message",
      data: { content: userText, attachments: [], interactionId: "inter-1" },
      id: "evt-3", timestamp: t, parentId: "evt-2",
    },
    { type: "assistant.turn_start", data: { turnId: "0", interactionId: "inter-1" }, id: "evt-4", timestamp: t, parentId: "evt-3" },
    {
      type: "assistant.message",
      data: {
        messageId: "msg-1", model: "gpt-5.6-luna", content: assistantText, toolRequests: [],
        interactionId: "inter-1", turnId: "0", phase: "final_answer", outputTokens: 7, requestId: "req-1",
      },
      id: "evt-5", timestamp: t, parentId: "evt-4",
    },
    { type: "assistant.turn_end", data: { turnId: "0" }, id: "evt-6", timestamp: t, parentId: "evt-5" },
    {
      type: "session.usage_checkpoint",
      data: { totalNanoAiu: 746350000, totalPremiumRequests: 0 },
      id: "evt-7", timestamp: t, parentId: "evt-6",
    },
  ];
  return lines.map((l) => JSON.stringify(l)).join("\n");
}

// Transcript-shaped request (VS Code chat export shape, trimmed).
export function transcriptRequest(text, opts = {}) {
  return {
    message: { text, parts: [{ kind: "text", value: text }] },
    response: [{ kind: "markdown", value: opts.response ?? "" }],
    modelId: opts.modelId ?? "copilot/auto",
    agent: opts.agent ?? "github.copilot.editsAgent",
    modeInfo: opts.modeInfo ?? { kind: "agent", permissionLevel: "default" },
    requestId: opts.requestId ?? "req-1",
    responseId: opts.responseId ?? "resp-1",
    result: {
      details: opts.details ?? "GPT-5.6 Luna • 0.8 credits",
      metadata: { agentId: opts.agent ?? "github.copilot.editsAgent", codeBlocks: opts.codeBlocks ?? [] },
    },
    timestamp: new Date().toISOString(),
    promptTokens: opts.promptTokens ?? 100,
    completionTokens: opts.completionTokens ?? 50,
    copilotCredits: opts.copilotCredits ?? 0.8,
    elapsedMs: opts.elapsedMs ?? 1200,
    timeSpentWaiting: opts.timeSpentWaiting ?? 300,
    variableData: opts.variableData ?? { variables: [] },
  };
}
