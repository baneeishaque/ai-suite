# Configuration, Authentication, and Permissions

> **Config directory:** `~/.gemini/antigravity-cli/` ·
> **Primary files:** `settings.json`, `keybindings.json` ·
> **Verified against:** Google Antigravity CLI documentation, 2026-10-27

## Configuration directory

| Path | Purpose |
| --- | --- |
| `~/.gemini/antigravity-cli/settings.json` | Persistent CLI settings |
| `~/.gemini/antigravity-cli/keybindings.json` | Custom keybindings |
| `~/.gemini/antigravity-cli/updater/` | Vendor self-updater state (`update.lock`, `last_check.timestamp`) |

The cask's `zap` stanza trashes the entire directory. The directory is separate from the Antigravity App's
`~/.gemini/config/` tree; do not copy settings between them blindly.

## Precedence

Highest wins:

1. Command-line flags (`--sandbox`, `--dangerously-skip-permissions`, `--mode`, `--model`, `--effort`).
2. `settings.json`.
3. Built-in defaults.

The `/config` overlay shows when a setting is overridden by a flag, for example
`Sandbox Mode on overridden by --sandbox`. A flag applies to the current session only; the on-disk value is
unchanged.

## `settings.json`

```json
{
    "$schema": "https://antigravity.google/schemas/v1/settings.json",
    "agentMode": "auto",
    "colorScheme": "tokyo night",
    "altScreenMode": "always",
    "toolPermission": "proceed-in-sandbox",
    "notifications": true,
    "enableTerminalSandbox": true
}
```

Adding `$schema` enables autocomplete and validation in editors such as VS Code.

### Full key reference

| Key | Type | Default | Purpose |
| --- | --- | --- | --- |
| `agentMode` | string | `""` | Startup execution mode: `""` (default), `"accept-edits"`, `"auto"`, or `"plan"` |
| `colorScheme` | string | `"terminal"` | Theme: `light`, `solarized light`, `colorblind-friendly light`, `dark`, `solarized dark`, `colorblind-friendly dark`, `tokyo night`, `terminal` |
| `altScreenMode` | string | `"default"` | `default` (inline conversation, full-screen overlays), `always`, or `never` |
| `toolPermission` | string | `"request-review"` | Global safety preset: `request-review`, `proceed-in-sandbox`, `always-proceed`, `strict` |
| `artifactReviewPolicy` | string | `"asks-for-review"` | `asks-for-review`, `agent-decides`, or `always-proceed` for plans and other artifacts |
| `notifications` | boolean | `false` | Terminal bell and desktop notification when the agent needs input or finishes |
| `showTips` | boolean | `true` | Show usage tips while the agent generates |
| `showFeedbackSurvey` | boolean | `true` | Show periodic quality surveys after tasks |
| `editor` | string | `"auto"` | External editor for artifacts and `Ctrl+G` prompt composition |
| `editorMode` | string | `"default"` | Prompt editing model: `default` or `vim` |
| `vimInsertFirst` | boolean | `false` | Start Vim mode in Insert; requires `editorMode: "vim"` |
| `allowNonWorkspaceAccess` | boolean | `false` | Allow reads and edits outside workspace folders |
| `enableTerminalSandbox` | boolean | `false` | Confine agent commands to the OS sandbox |
| `useG1Credits` | boolean | `false` | Spend AI credits after plan quota is exhausted; not for business accounts |
| `verbosity` | string | `"medium"` | Rendering detail: `high`, `medium`, or `low` |
| `runningLightSpeed` | string | `"medium"` | Progress animation: `fast`, `medium`, `slow`, or `off` |
| `copyOnSelect` | boolean | `true` | In alt-screen mode, copy on mouse selection |
| `hideActiveItems` | boolean | `false` | Hide the active subagent and background task list |
| `pickerGrouping` | string | `"none"` | `/resume` picker layout: `none` or `grouped` by workspace |
| `queuedMessages` | string | `"queue"` | Message sent while busy: `queue` or `send-immediately` |
| `clearScrollbackOnResize` | boolean | `true` | Clear terminal scrollback when inline mode redraws |
| `disableSlashCommands` | boolean | `false` | In headless mode, send leading-`/` prompts literally |
| `historySize` | integer | `2000` | Prompt history entries kept; `-1` keeps all, `0` clears |
| `model` | string | `""` | Last model selected with `/model`, stored by label |
| `modelProvider` | string | `""` | `"gemini"` routes requests to the Gemini API using `GEMINI_API_KEY` |
| `trustedWorkspaces` | string[] | `[]` | Folders you approved during workspace trust prompts |
| `useTerminalCursor` | boolean | `false` | Use the terminal's cursor shape instead of a block cursor |
| `permissions` | object | — | Allow, ask, and deny rules for tools |
| `statusLine` | object | — | Custom status line script |
| `title` | object | — | Custom terminal title script |
| `sandboxProxy` | object | — | HTTP proxy for sandboxed commands |
| `customModelsConfig` | object | — | Extra models for Gemini API key setups |
| `gcp` | object | — | Saved Google Cloud project and location |

`Enable Telemetry` in `/config` has no `settings.json` key; the choice is stored with your account.

## Object-valued settings

### `permissions`

```json
{
    "permissions": {
        "allow": [
            "command(git)",
            "command(regex:npm run (build|lint|test))",
            "write_file(src/)"
        ],
        "ask": [
            "command(rm)"
        ],
        "deny": [
            "write_file(.env)"
        ]
    }
}
```

Rules use the form `action(target)`. Targets can be literal paths or commands, or regular expressions with
the `regex:` prefix. Deny rules apply in every permission preset. See
[Permissions](#permissions-1) for the preset interaction.

### `statusLine`, `title`, `sandboxProxy`, `customModelsConfig`, `gcp`

These keys take objects whose schemas are documented in Google's CLI settings reference. Keep them as
objects; do not flatten them into strings. The `gcp` object is written automatically when you sign in with
**Use a Google Cloud project**.

## `keybindings.json`

| Property | Detail |
| --- | --- |
| Location | `~/.gemini/antigravity-cli/keybindings.json` |
| Editor | `/keybindings`, or edit the JSON directly |
| Reset | Delete the file |
| Shape | Action name to an array of key combinations |
| Disabling an action | Set its array to `[]` |
| Malformed file | Valid parts load; broken actions fall back to defaults |
| Cannot be disabled | `cli.exit` and `cli.enter` |

Example:

```json
{
    "cli.clear_screen": ["ctrl+l"],
    "prompt.insert_newline": ["shift+enter", "ctrl+j"],
    "view.review_artifact": ["ctrl+r"]
}
```

See [usage.md](usage.md) for the default key tables and their action names.

## Execution modes

| Mode | File edits | Commands | Best for |
| --- | --- | --- | --- |
| `default` | Pauses for inline diff review | Asks before running | Sensitive changes, careful refactors |
| `accept-edits` | Auto-approves inside the workspace | Asks before running | Trusted code, rapid iteration |
| `auto` (Preview) | Auto-approves inside the workspace | Runs in the sandbox; safe commands outside it auto-run, risky ones prompt | Autonomous workflows |
| `plan` | Read-only investigation | Read-only | Unfamiliar code, multi-step design |

- Cycle during a session with `Shift+Tab`: `default` > `accept-edits` > `auto` > `plan`.
- Override at launch with `agy --mode=accept-edits`, `--mode=auto`, or `--mode=plan`.
- Persist with `agentMode` in `settings.json`.
- `auto` requires the terminal sandbox and is unavailable to business and enterprise accounts. Where it is
  unavailable, the cycle skips it.

Explicit allow, ask, and deny rules and global overrides take precedence over the execution mode.

## Permissions

### Presets

| `toolPermission` | Behaviour |
| --- | --- |
| `request-review` | Prompts for writes, shell commands, web requests, and MCP tools unless an allow rule matches |
| `proceed-in-sandbox` | Runs commands without prompting when they execute inside the sandbox |
| `always-proceed` | Runs commands, web requests, and MCP tools unless an ask or deny rule matches |
| `strict` | Prompts before every tool action, including reads, even when an allow rule matches |

Deny rules apply in every preset.

### Rule syntax

| Example | Matches |
| --- | --- |
| `command(git)` | The `git` command |
| `command(regex:npm run (build\|lint\|test))` | Commands matching the regular expression |
| `write_file(src/)` | Writes under `src/` |

Use `/permissions` for the interactive manager. In headless mode there is no prompt, so pre-grant what the
run needs in `permissions.allow`, or pass `--dangerously-skip-permissions` when the environment is fully
trusted.

## Authentication

Antigravity uses one authentication layer across the App, CLI, IDE extensions, and SDK. The CLI stores tokens
in the OS keyring and reuses them silently.

| Method | Setup | Notes |
| --- | --- | --- |
| Personal Google account | Launch `agy`, complete browser OAuth | Free, Pro, and Ultra plans |
| Gemini Enterprise | Choose **Business account** > **Continue with Google Cloud**, or WIF | Requires a GCP project and region |
| Remote SSH OAuth | Launch `agy` over SSH, open the printed URL locally, paste the code back | For headless servers without a local browser |
| Gemini API key | `modelProvider: "gemini"` plus `GEMINI_API_KEY` | Both are required; the env var alone does nothing |
| Application Default Credentials | `gcloud auth application-default login`, then `AGY_ADC_AUTH=true` | For automated enterprise environments |

### Gemini API key

```json
{
    "modelProvider": "gemini"
}
```

```bash
export GEMINI_API_KEY="your-api-key"
```

Optional custom endpoint:

```bash
export GOOGLE_GEMINI_BASE_URL="https://your-endpoint.example.com"
```

Important behaviours:

- `GOOGLE_API_KEY` is **not** read; only `GEMINI_API_KEY`.
- `.env` files are **not** loaded; export the variable in the shell or profile.
- If `modelProvider` is `gemini` and `GEMINI_API_KEY` is unset, the CLI exits at startup.
- `/logout` has no effect under API-key auth because no session is stored.
- The key is validated only as non-empty at startup; an invalid key fails on the first request.

### Application Default Credentials

```bash
gcloud auth application-default login --project "$GCP_PROJECT"
export AGY_ADC_AUTH=true
export GOOGLE_CLOUD_QUOTA_PROJECT="$GCP_PROJECT"   # optional
export GOOGLE_CLOUD_LOCATION="us-central1"         # optional
```

Unset `AGY_ADC_AUTH` and restart the terminal to sign out of ADC.

### Logout

```text
/logout
```

This disconnects the profile and purges authentication tokens from the keyring. It does not delete
`settings.json`.

## Environment variables

| Variable | Used by | Effect |
| --- | --- | --- |
| `GEMINI_API_KEY` | CLI | Gemini API key; only read when `modelProvider` is `gemini` |
| `GOOGLE_GEMINI_BASE_URL` | CLI | Redirect Gemini API requests to a compatible endpoint |
| `AGY_ADC_AUTH` | CLI | Set to `true` to authenticate with Application Default Credentials |
| `GOOGLE_CLOUD_QUOTA_PROJECT` | CLI | Optional quota project for ADC |
| `GOOGLE_CLOUD_LOCATION` | CLI | Optional ADC location |
| `AGY_CLI_DISABLE_AUTO_UPDATE` | CLI | Set to `true` to disable the vendor self-updater |
| `EDITOR` | CLI | Fallback editor for `Ctrl+G` and artifact viewing when `editor` is `auto` |

The Antigravity **SDK** uses additional variables such as `GOOGLE_GENAI_USE_VERTEXAI`,
`GOOGLE_CLOUD_PROJECT`, and `GOOGLE_CLOUD_LOCATION`. Do not assume those configure the CLI.

## Workspace trust

The CLI records trusted folders in `trustedWorkspaces`. Trust controls whether the agent may index and act
inside a directory. To revoke trust, remove the entry from `settings.json` or delete the file. A prompt that
mentions `outside workspace` means the path is not covered by the current workspace roots; use `/add-dir`
or `--add-dir` rather than enabling `allowNonWorkspaceAccess` casually.

## Related

- [README.md](README.md) — overview
- [installation.md](installation.md) — install and removal
- [usage.md](usage.md) — commands, shortcuts, headless mode
- [troubleshooting.md](troubleshooting.md) — keyring and updater problems
