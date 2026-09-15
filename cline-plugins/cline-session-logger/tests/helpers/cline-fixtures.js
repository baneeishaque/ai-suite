// Cline hook payload factories — mirrors opencode-plugins/tests/helpers/fixtures.ts.
// Shapes match the Cline hooks input contract (taskId, hookName, timestamp
// ms-string, workspaceRoots, model{provider,slug}, hook-specific field).
export const MARKERS = {
  userText: "Hello cline logger",
  secondUserText: "Second cline prompt",
  toolResult: "file contents here",
};

let seq = 0;

export function base(taskId, hookName, extra = {}) {
  return {
    taskId,
    hookName,
    timestamp: String(Date.now() + seq++),
    workspaceRoots: [],
    userId: "test-user",
    model: { provider: "anthropic", slug: "claude-sonnet-4-5" },
    ...extra,
  };
}

export const taskStart = (taskId, task = "test task", opts = {}) => base(taskId, "TaskStart", {
  taskStart: {
    task,
    taskMetadata: {
      taskId,
      ...(opts.ulid ? { ulid: opts.ulid } : {}),
      initialTask: task,
      ...(opts.extraIds ?? {}),
    },
  },
});

export const taskResume = (taskId) => base(taskId, "TaskResume", {
  taskResume: { task: "resumed" },
});

export const userPrompt = (taskId, prompt = MARKERS.userText) => base(taskId, "UserPromptSubmit", {
  userPromptSubmit: { prompt },
});

export const preTool = (taskId, tool = "read_file", parameters = { path: "src/a.ts" }) =>
  base(taskId, "PreToolUse", { preToolUse: { tool, parameters } });

export const postTool = (taskId, tool = "read_file", opts = {}) => base(taskId, "PostToolUse", {
  postToolUse: {
    tool,
    parameters: opts.parameters ?? { path: "src/a.ts" },
    result: opts.result ?? MARKERS.toolResult,
    success: opts.success ?? true,
    durationMs: opts.durationMs ?? 12,
  },
});

export const taskComplete = (taskId, opts = {}) => base(taskId, "TaskComplete", {
  taskComplete: {
    task: "done",
    ...(opts.taskMetadata ? { taskMetadata: opts.taskMetadata } : {}),
  },
});

export const taskCancel = (taskId, opts = {}) => base(taskId, "TaskCancel", {
  taskCancel: {
    task: "cancelled",
    ...(opts.taskMetadata ? { taskMetadata: opts.taskMetadata } : {}),
  },
});

export const preCompact = (taskId) => base(taskId, "PreCompact", {
  preCompact: { conversationLength: 100, estimatedTokens: 5000 },
});

export const unknownHook = (taskId) => base(taskId, "SomeFutureHook", {});
