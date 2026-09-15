// Claude hook payload factories.
// Shapes match the Claude Code hooks contract (session_id, cwd,
// hook_event_name, transcript_path, per-event fields).
export const MARKERS = {
  userText: "Hello claude logger",
  toolResponse: "File contents here",
  lastAssistant: "Done, all green.",
};

let seq = 0;

export function base(sessionId, hook_event_name, extra = {}) {
  return {
    session_id: sessionId,
    transcript_path: "",
    cwd: "",
    hook_event_name,
    ...extra,
  };
}

export const sessionStart = (sessionId, source = "startup", extra = {}) =>
  base(sessionId, "SessionStart", { source, model: "claude-opus-4-6", ...extra });

export const userPrompt = (sessionId, prompt = MARKERS.userText) =>
  base(sessionId, "UserPromptSubmit", { prompt });

export const preTool = (sessionId, tool = "Read", input = { file_path: "src/a.ts" }, toolUseId = "tool-1", extra = {}) =>
  base(sessionId, "PreToolUse", { tool_name: tool, tool_input: input, tool_use_id: toolUseId, ...extra });

export const postTool = (sessionId, tool = "Read", input = { file_path: "src/a.ts" }, response = MARKERS.toolResponse, toolUseId = "tool-1", extra = {}) =>
  base(sessionId, "PostToolUse", {
    tool_name: tool, tool_input: input, tool_use_id: toolUseId, tool_response: response, duration_ms: 120, ...extra,
  });

export const postToolFailure = (sessionId, tool = "Bash", input = { command: "exit 1" }, error = "Exit code 1", extra = {}) =>
  base(sessionId, "PostToolUseFailure", {
    tool_name: tool, tool_input: input, tool_use_id: "tool-9", error, ...extra,
  });

export const preCompact = (sessionId, trigger = "auto") => base(sessionId, "PreCompact", { trigger });

export const postCompact = (sessionId, trigger = "auto") => base(sessionId, "PostCompact", { trigger });

export const subagentStart = (sessionId, agentId = "agent-1", agentType = "Explore") =>
  base(sessionId, "SubagentStart", { agent_id: agentId, agent_type: agentType });

export const subagentStop = (sessionId, agentId = "agent-1", agentType = "Explore", extra = {}) =>
  base(sessionId, "SubagentStop", {
    agent_id: agentId, agent_type: agentType, stop_hook_active: false,
    last_assistant_message: MARKERS.lastAssistant, ...extra,
  });

export const stop = (sessionId, extra = {}) =>
  base(sessionId, "Stop", { stop_hook_active: false, last_assistant_message: MARKERS.lastAssistant, ...extra });

export const stopFailure = (sessionId, error = "rate_limit") =>
  base(sessionId, "StopFailure", { error, last_assistant_message: "" });

export const sessionEnd = (sessionId, reason = "other") => base(sessionId, "SessionEnd", { reason });

export const taskCreated = (sessionId, subject = "Do the thing") =>
  base(sessionId, "TaskCreated", { subject });

export const taskCompleted = (sessionId, subject = "Do the thing") =>
  base(sessionId, "TaskCompleted", { subject });

export const modelSwitch = (sessionId, to = "claude-opus-4-6", from = "claude-sonnet-4-5") =>
  base(sessionId, "PostModelSwitch", { to_model: to, from_model: from });

export const unknownEvent = (sessionId) => base(sessionId, "SomeFutureEvent", {});

// Transcript envelope builders (real ~/.claude/projects shapes, trimmed).
export function userEnvelope(text, opts = {}) {
  return {
    parentUuid: opts.parentUuid ?? null,
    isSidechain: false,
    type: "user",
    message: { role: "user", content: text },
    uuid: opts.uuid ?? "uuid-user-1",
    timestamp: "2026-08-20T09:34:31.846Z",
    sessionId: opts.sessionId ?? "sess-1",
    version: "2.1.235",
    gitBranch: "main",
    cwd: "/tmp/ws",
  };
}

export function assistantEnvelope(text, opts = {}) {
  const blocks = [{ type: "text", text }];
  for (const call of opts.toolCalls ?? []) {
    blocks.push({ type: "tool_use", id: call.id, name: call.name, input: call.input ?? {} });
  }
  return {
    parentUuid: opts.parentUuid ?? "uuid-user-1",
    isSidechain: false,
    type: "assistant",
    message: { role: "assistant", content: blocks },
    uuid: opts.uuid ?? "uuid-asst-1",
    timestamp: "2026-08-20T09:34:40.000Z",
    model: opts.model ?? "claude-opus-4-6",
    usage: opts.usage ?? { input_tokens: 100, output_tokens: 50 },
    sessionId: opts.sessionId ?? "sess-1",
    version: "2.1.235",
    gitBranch: "main",
    cwd: "/tmp/ws",
  };
}
