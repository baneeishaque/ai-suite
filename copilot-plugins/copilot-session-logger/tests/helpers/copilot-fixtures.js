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

export const sessionStart = (sessionId, source = "new") => base(sessionId, "SessionStart", { source });

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
