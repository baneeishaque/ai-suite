# Usage — Interactive TUI, Commands, and Headless Mode

> **Binary:** `agy` · **Interactive:** `agy` · **One-shot:** `agy -p "<prompt>"` ·
> **Docs verified:** 2026-10-27

## Launch patterns

| Command | Behaviour |
| --- | --- |
| `agy` | Start the interactive TUI in the current directory |
| `agy "prompt"` | Start the TUI with an initial prompt |
| `agy -p "prompt"` | Run one prompt non-interactively and print the response |
| `agy --continue` | Continue the most recent conversation |
| `agy --conversation <id>` | Resume a specific conversation |
| `agy models` | List available model slugs |
| `agy agents` | List available agents |
| `agy --version` | Print the installed version |
| `agy --help` | Print the installed build's flag reference |

The first launch in a directory asks you to trust the workspace before indexing it.

## Interactive TUI basics

| Action | How |
| --- | --- |
| Send a prompt | Type, then `Enter` |
| Insert a newline | `Shift+Enter` or `Ctrl+J` |
| File-path completion | Type `@` |
| Run a shell command directly | Start the prompt with `!` |
| Clear the prompt | `Esc` `Esc` when nothing is streaming |
| Help | Type `?` |
| Slash-command menu | Type `/` |
| Review artifacts and diffs | `Ctrl+R` |
| Approve a pending subagent action | `Ctrl+K` |
| Jump to the next waiting subagent | `Alt+J` |
| Cycle execution mode | `Shift+Tab` |
| Exit | `/exit`, `Ctrl+D` on an empty prompt, or `Ctrl+C` |

On exit, the CLI prints the exact command needed to resume that session.

## Slash commands

| Command | Category | Purpose |
| --- | --- | --- |
| `/add-dir <path>` | Utilities | Add a directory to the active workspace |
| `/agents` | Tools & Tasks | Open Agent Manager; switch agents and monitor background subagents |
| `/artifact` | Tools & Tasks | Open the Artifact Review panel |
| `/boost <task>` | Reasoning | Run on-demand multi-agent deep reasoning loops |
| `/browser <task>` | Tools & Tasks | Delegate browsing, UI verification, and in-browser debugging |
| `/btw <query>` | Utilities | Ask a side question without interrupting the main conversation |
| `/changelog` | Utilities | Open the interactive release-notes viewer |
| `/clear`, `/new` | Utilities | Clear the terminal and reset the conversation context |
| `/codesearch <query>`, `/cs`, `/search` | Utilities | Open the interactive code search panel |
| `/config`, `/settings` | Configurations | Open the interactive settings editor |
| `/context` | Utilities | Show context usage |
| `/copy [n\|btw]` | Utilities | Copy the last, n-th, or latest `/btw` response |
| `/credits` | Account | Show remaining G1 credits and purchase links |
| `/diff` | Utilities | Open the interactive diff viewer |
| `/effort [level]` | Configurations | Set or inspect reasoning effort |
| `/exit`, `/quit` | Core | Close the TUI and restore the shell |
| `/feedback` | Utilities | Open the feedback panel |
| `/fork`, `/branch` | Conversations | Clone the current thread into a parallel session |
| `/goal <objective>` | Reasoning | Run autonomously until the goal is verified complete |
| `/grill-me [task]` | Planning | Interview you one question at a time before starting |
| `/help` | Utilities | Open the help panel |
| `/hooks` | Tools & Tasks | Browse active pre-flight and post-format hooks |
| `/keybindings` | Configurations | Open the keyboard shortcut editor |
| `/learn [instruction]` | Tools & Tasks | Turn session corrections into rules or skills via a proposal |
| `/logout` | Account | Disconnect and purge tokens from the keyring |
| `/mcp` | Tools & Tasks | Open the MCP server manager |
| `/model` | Configurations | Choose a model; `/model <model> <prompt>` runs one prompt on another model |
| `/open <path>` | Utilities | Open a path in the system editor |
| `/permissions` | Configurations | Open the tool permissions manager |
| `/plan [task]` | Planning | Draft a reviewable implementation plan |
| `/plugin`, `/plugins` | Tools & Tasks | Open the plugins manager or run `install`, `uninstall`, `enable`, `disable`, `list` |
| `/rename <name>` | Conversations | Rename the current thread |
| `/remote-control [on\|off]` | Utilities | Toggle Remote Control for the session |
| `/resume`, `/switch`, `/conversation` | Conversations | Open the conversation picker |
| `/rewind`, `/undo` | Conversations | Roll back to a previous message |
| `/schedule <when> <task>` | Tools & Tasks | Set a one-shot timer or recurring cron schedule |
| `/skills` | Tools & Tasks | Browse loaded skills; `/skills reload` re-reads them from disk |
| `/statusline` | Configurations | Customize the status bar |
| `/tasks` | Tools & Tasks | Monitor background shell execution logs |
| `/teamwork-preview <task>`, `/teamwork` | Reasoning | Launch collaborative multi-agent teams (paid plans) |
| `/title [on\|off]` | Configurations | Toggle or set terminal title updates |
| `/usage`, `/quota` | Utilities | Show model quota usage |
| `/voice`, `/record` | Utilities | Dictate a prompt |

## Keyboard shortcuts

### Global

| Key | Action name | Behaviour |
| --- | --- | --- |
| `Esc` | `cli.escape` | Close panels, halt streams, or clear an empty prompt |
| `Ctrl+C` | `cli.exit` | Terminate the session; confirms if the agent is working |
| `Ctrl+D` | `cli.exit` | Exit when the prompt is empty |
| `Ctrl+L` | `cli.clear_screen` | Refresh and clear the terminal buffer |

### Prompt focus

| Key | Action name | Behaviour |
| --- | --- | --- |
| `Enter` | `cli.enter` | Submit the prompt or menu selection |
| `Shift+Enter`, `Ctrl+J` | `prompt.insert_newline` | Insert a newline without submitting |
| `Shift+Tab` | `cli.cycle_mode` | Cycle `default` > `accept-edits` > `auto` > `plan` |
| `Ctrl+V` | `edit.paste` | Paste media or clipboard blocks |
| `Ctrl+O` | `view.toggle_trajectory` | Expand or collapse tool reasoning |
| `Ctrl+R` | `view.review_artifact` | Open Artifact Review |
| `Ctrl+G` | `edit.open_editor` | Compose the prompt in `$EDITOR` |
| `Alt+J` | `subagent.jump_to_waiting` | Focus the next subagent awaiting confirmation |
| `Ctrl+K` | `subagent.approve_fast` | Approve the pending subagent action |
| `Ctrl+A` / `Ctrl+E` | — | Move to the start / end of the line |
| `Ctrl+_`, `Ctrl+Shift+-` | `edit.undo` | Undo the last text edit |
| `Ctrl+Shift+Z` | `edit.redo` | Redo the last undone edit |
| `Ctrl+D` | — | Forward delete when the prompt is non-empty |
| `F5` | `voice.start_dictation` | Start or stop dictation |

### Navigation and scrolling

| Key | Action name | Behaviour |
| --- | --- | --- |
| `Up` / `Down` | `navigation.up` / `navigation.down` | Move the selection by one item |
| `PgUp`, `Shift+Up` | `navigation.page_up`, `navigation.half_page_up` | Scroll up one page or half page |
| `PgDn`, `Shift+Down` | `navigation.page_down`, `navigation.half_page_down` | Scroll down one page or half page |
| `Left` / `Right` | `navigation.left` / `navigation.right` | Change pages in multi-page panels |
| `Tab` | `navigation.tab` | Accept the highlighted slash-command autofill |

### Tool confirmations

| Key | Action name | Behaviour |
| --- | --- | --- |
| `y` | `confirm.yes` | Approve the proposed tool, command, or artifact |
| `n` | `confirm.no` | Reject it |
| `A` | — | In the Review panel, approve all generated artifacts |

### Additional keys from the settings page

| Key | Behaviour |
| --- | --- |
| `Ctrl+Z` | Suspend the CLI to the background |
| `e` | Edit the proposed terminal command in your editor |
| `Ctrl+Y` | Yank (copy) selected text |
| `Ctrl+Home` / `Ctrl+End` | Jump to the top / bottom of the TUI view |

## CLI flags

| Flag | Default | Purpose |
| --- | --- | --- |
| `--mode` | `""` | Execution mode: `accept-edits`, `auto`, or `plan` |
| `--model` | — | Model slug for this session |
| `--effort` | — | Reasoning effort: `low` through `max`, depending on the model |
| `--agent` | — | Agent for this session |
| `--add-dir` | `[]` | Add a workspace directory; repeatable |
| `-c`, `--continue` | `false` | Continue the most recent conversation |
| `--conversation` | — | Resume a conversation by ID |
| `-i`, `--prompt-interactive` | — | Run an initial prompt and keep the session interactive |
| `-p`, `--print`, `--prompt` | — | Run one prompt non-interactively |
| `--output-format` | `text` | `text`, `json`, or `stream-json` |
| `--input-format` | `text` | `text` or `stream-json` (prompts on stdin) |
| `--json-schema` | — | Schema string, schema file path, or primitive type name |
| `--print-timeout` | See note | Time limit for print mode |
| `--disable-slash-commands` | `false` | In print mode, send leading-`/` prompts literally |
| `--sandbox` | `false` | Enable terminal sandbox restrictions |
| `--dangerously-skip-permissions` | `false` | Auto-approve every tool request |
| `--remote-control` | `false` | Open a Remote Control connection at startup |
| `--project` | — | Project ID or name for the session |
| `--new-project` | `false` | Create a new project for the session |
| `--log-file` | — | Override the CLI log file path |

> **Timeout documentation conflict:** the CLI reference lists `--print-timeout` default as `0s` ("waits
> until the turn completes"), while the headless guide says a run waits up to five minutes and its flag
> table says `5m`. Confirm the effective default with `agy --help` for your installed build.

## Headless (print) mode

Headless mode sends one prompt, returns the result, and exits. It is the integration surface for scripts
and CI.

```bash
agy -p "In one sentence, what is a git rebase?"
```

`stdout` carries the response; `stderr` carries diagnostics, authentication prompts, progress, and
permission notices.

```bash
answer=$(agy -p "Name three version control systems, comma-separated.")
```

Headless runs use cached credentials. Authenticate once interactively, or configure API-key/ADC auth for
non-interactive environments. Without credentials, a headless run exits with `authentication required`
instead of hanging.

### Output formats

| `--output-format` | `stdout` shape | Use for |
| --- | --- | --- |
| `text` | Response text only | Human-readable output, simple scripts |
| `json` | One JSON object on completion | Result plus metadata |
| `stream-json` | Newline-delimited JSON events | Live progress, tool calls, token usage |

The JSON envelope contains:

| Field | Type | Meaning |
| --- | --- | --- |
| `conversation_id` | string | Conversation ID for resuming |
| `status` | string | `SUCCESS`, `ERROR`, `CANCELED`, `INTERRUPTED`, `INVALID`, `WAITING`, or `RUNNING` |
| `response` | string | Free-text response |
| `error` | string | Present on failure |
| `duration_seconds` | number | Wall-clock duration |
| `num_turns` | number | User turns in the conversation |
| `structured_output` | object | Parsed schema output when `--json-schema` is used |
| `json_schema` | object | The enforced schema |
| `usage` | object | `input_tokens`, `output_tokens`, `thinking_tokens`, `cache_read_tokens`, `total_tokens` |

Parse with `jq`:

```bash
agy -p "Name three version control systems, comma-separated." \
  --output-format json | jq -r '.response'
```

### Structured output

```bash
agy -p "Parse v2.14.3 into integer major, minor, and patch fields." \
  --output-format json \
  --json-schema '{"type":"object","properties":{"major":{"type":"integer"},"minor":{"type":"integer"},"patch":{"type":"integer"}},"required":["major","minor","patch"]}' \
  | jq '.structured_output'
```

`--json-schema` also accepts a path to a `.json` schema file or a primitive type name (`string`, `number`,
`integer`, `boolean`).

### Streaming events

`--output-format stream-json` emits one JSON object per line:

| Event | Emitted | Payload |
| --- | --- | --- |
| `init` | Once at start | `cwd`, `tools`, `permission_mode`, optional `model`, `agent`, `json_schema` |
| `step_update` | Per step transition or text delta | `step_index`, `state`, `step_type`, `text_delta`, `usage`, `tool_info`, `subagent_info` |
| `result` | Once at end | Same shape as the JSON envelope |

Concatenate streamed text:

```bash
agy -p "Explain merge conflicts in two sentences." --output-format stream-json \
  | jq -j 'select(.event=="step_update") | .step_update.text_delta // empty'
```

Read cumulative token usage:

```bash
agy -p "Summarize optimistic locking." --output-format stream-json \
  | jq 'select(.event=="result") | .result.usage'
```

### Multi-turn streaming over stdin

`--input-format stream-json` keeps one process alive and accepts prompts on stdin. It requires
`--output-format stream-json`.

```bash
printf '%s\n' \
  '{"event":"user","message":{"content":"Reply with exactly: apple."}}' \
  '{"event":"user","message":{"content":"What word did I ask you to repeat?"}}' \
  | agy --input-format stream-json --output-format stream-json \
  | jq -r 'select(.event=="result") | "\(.result.num_turns): \(.result.response)"'
```

Rules and pitfalls:

- Close `stdin` to end the session; the process exits after the current turn completes.
- Do not pass a prompt with `-p` in this mode; prompts come only from stdin.
- `--output-format json` or `text` with streaming input loses every turn except the last.
- CLI-handled slash commands such as `/model` and `/usage` break the event stream; run them as separate
  `agy -p /model` invocations.
- `num_turns`, `duration_seconds`, and `usage` are cumulative for the session; `response` is per turn.
- Unsupported message shapes end the session with an error. Unknown event names are skipped with a warning.

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success, including soft-denied tools that did not block the response |
| Non-zero | The run failed to produce a response; details are on `stderr` and in `status` / `error` |

In headless mode, tools that would prompt are soft-denied unless allowed ahead of time. Reading and writing
inside the workspace is auto-allowed; shell commands default to **Ask** and are denied without a prompt
unless you add a `permissions.allow` rule or pass `--dangerously-skip-permissions`.

### CI example

```bash
#!/usr/bin/env bash
set -euo pipefail

result=$(agy -p "Name three popular version control systems, comma-separated." \
  --output-format json \
  --print-timeout 10m)

status=$(echo "$result" | jq -r '.status')
if [[ "$status" != "SUCCESS" ]]; then
  echo "Agent run failed: $(echo "$result" | jq -r '.error')" >&2
  exit 1
fi

echo "$result" | jq -r '.response' > result.txt
```

## Models, effort, and agents

```bash
agy models
agy agents
agy -p "Reverse the string antigravity." --model gemini-3.8-flash-medium
agy -p "Outline a caching plan." --effort high
agy -p "Review this function." --agent <agent-name>
```

Unlike the interactive UI, headless mode does **not** silently fall back when `--model` names an unknown
model. It exits non-zero with an `ERROR` status so a pinned pipeline fails loudly.

## Conversation management

| Task | Command |
| --- | --- |
| Continue the most recent conversation | `agy --continue` |
| Resume by ID | `agy --conversation <id>` |
| Pick a previous thread | `/resume` |
| Clone the current thread | `/fork` |
| Roll back | `/rewind` or `/undo` |
| Rename | `/rename <name>` |
| Clear and start over | `/clear` |
| Find the resume command | Printed automatically on exit |

## Related

- [README.md](README.md) — overview
- [configuration.md](configuration.md) — settings, auth, permissions, modes
- [troubleshooting.md](troubleshooting.md) — common failures
