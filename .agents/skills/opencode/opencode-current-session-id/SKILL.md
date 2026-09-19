---
name: opencode-current-session-id
description: Composer — discover the current opencode session ID and title from the logger logs
category: OpenCode
---

# OpenCode Current Session ID (v1)

## Composition Rationale

This skill is a **composer**: it does NOT re-implement glob-sorting or YAML parsing. It sequences two base skills:

1. [`file-glob-sort-by-mtime`](../general/file/file-glob-sort-by-mtime/SKILL.md) — finds the newest `.yaml` file in `.opencode/logs/`
2. [`yaml-field-extract`](../general/yaml-field-extract/SKILL.md) — extracts `session.id` and `title` from the YAML header

The composer's value-add: orchestrating the pipeline, resolving relative script paths, and cross-verifying the state file exists.

## When to Use

- You need to know the current opencode session ID programmatically
- You are composing a larger workflow that needs the session ID for traceability

## Environment & Dependencies

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.12+ | Stdlib only |
| PyYAML | any | Required by yaml-field-extract (PEP 723 inline metadata) |
| `.opencode/logs/` | — | Must exist (created by opencode logger plugin) |

## CLI Contract

| Argument | Required | Description |
|----------|----------|-------------|
| _(none)_ | — | Runs the full pipeline with auto-discovered repo root and log dir |
| `--log-dir PATH` | No | Override `.opencode/logs/` directory (default: `<repo-root>/.opencode/logs` or `$OPENCODE_LOGS_DIR`) |
| `--repo-root PATH` | No | Override repo root discovery (default: `$OPENCODE_REPO_ROOT` / `$AI_SUITE_ROOT`, then `git rev-parse --show-toplevel`, then legacy `parents[4]`) |
| `--json` | No | Emit single-line JSON instead of human-readable text |

**Output (text, default):**
```
Session ID: ses_XXXXXXXXXXXXX
Title: My Session Title
State file: exists
```

**Exit codes:**
- `0` — session ID found, title and state file verified
- `1` — any pipeline step failed (missing log, missing key, etc.)

**Output (`--json`):**
```json
{"session_id": "ses_XXXXXXXXXXXXX", "title": "My Session Title", "state": "exists", "yaml_path": "<path>", "log_dir": "<path>"}
```
`title` is `null` when the YAML header has no `title` key.

## Protocol

1. Run `python3 scripts/find-current-session.py`
2. Read stdout for session ID, title, and state file presence.

## Edge Cases

- **No YAML logs exist**: exits 1 with "could not find newest YAML log"
- **YAML header missing session.id**: exits 1
- **No state file**: still succeeds (reports "missing")
- **Symlinked log dir**: follows symlinks via `Path.rglob`

## Prohibited Actions

- Do NOT re-derive the sort or YAML extraction logic inline — always delegate to the base skill scripts.
- Do NOT hardcode log directory paths — use `.opencode/logs/` relative to repo root.

## Script Reference

`find-current-session.py`:
1. Resolves base script paths relative to its own location
2. Runs `sort-by-mtime.py` on `.opencode/logs/` with glob `*.yaml` and `--limit 1`
3. Parses JSON Lines output to get the newest file path
4. Runs `extract-field.py` twice: once for `session.id`, once for `title`
5. Checks for `.opencode/logs/<sid>.state.json`
6. Prints results

## Composition by Lower-Level Skills

| Primitive | Composition Mechanism |
|-----------|----------------------|
| `file-glob-sort-by-mtime` | `sort-by-mtime.py --dir .opencode/logs --glob *.yaml --limit 1` → newest path |
| `yaml-field-extract` | `extract-field.py --file <path> --key session.id` → session ID |

## Related Skills

- [`file-glob-sort-by-mtime`](../general/file/file-glob-sort-by-mtime/SKILL.md) — base for finding the newest log file
- [`yaml-field-extract`](../general/yaml-field-extract/SKILL.md) — base for extracting YAML header fields
- [`opencode-installed-plugin-lookup`](../opencode-installed-plugin-lookup/SKILL.md) — consumer of the logger-location convention (.opencode/logs/)
