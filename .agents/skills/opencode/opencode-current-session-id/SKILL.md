---
name: opencode-current-session-id
description: Composer — discover the current opencode session ID and title from the logger logs
category: OpenCode
---

# OpenCode Current Session ID (v1)

## Composition Rationale

This skill is a **composer**: it does NOT re-implement glob-sorting or YAML parsing. It sequences two base skills:

1. [`file-glob-sort-by-mtime`](../../general/file/file-glob-sort-by-mtime/SKILL.md) — finds the newest `.yaml` file in
   `.opencode/logs/`
2. [`yaml-field-extract`](../../general/yaml-field-extract/SKILL.md) — extracts `session.id` and `title` from the YAML
   header

The composer's value-add: orchestrating the pipeline, resolving relative script paths, and cross-verifying the state
file exists.

## When to Use

- You need to know the current opencode session ID programmatically
- You are composing a larger workflow that needs the session ID for traceability

## Environment & Dependencies

| Requirement | Version | Notes |
| ------------- | --------- | ------- |
| Python | 3.12+ | Stdlib only |
| PyYAML | any | Required by yaml-field-extract (PEP 723 inline metadata) |
| `.opencode/logs/` | — | Must exist (created by opencode logger plugin) |

## CLI Contract

| Argument | Required | Description |
| ---------- | ---------- | ------------- |
| _(none)_ | — | Runs the full pipeline with auto-discovered repo root and log dir |
| `--log-dir PATH` | No | Override `.opencode/logs/` directory (default: `<repo-root>/.opencode/logs` or `$OPENCODE_LOGS_DIR`) |
| `--repo-root PATH` | No | Override repo root discovery (default: `$OPENCODE_REPO_ROOT` / `$AI_SUITE_ROOT`, then `git rev-parse --show-toplevel`, then legacy `parents[4]`) |
| `--json` | No | Emit single-line JSON instead of human-readable text |
| `--state {exists,missing,any}` | No | Gate on state-file presence (default: `any`; mismatch exits 2) |
| `--since ISO_TIMESTAMP` | No | Filter sessions by `st_mtime >= timestamp` (e.g. `2026-09-19T10:00:00`) |
| `--dry-run` | No | Print discovered paths (repo_root, log_dir, base scripts) as JSON and exit without extractors |

**Output (text, default):**

```text
Session ID: ses_XXXXXXXXXXXXX
Title: My Session Title
State file: exists
```

**Exit codes:**

- `0` — session ID found (and state gate satisfied when `--state` given)
- `1` — any pipeline step failed (missing log, missing key, etc.)
- `2` — session found but `--state` gate mismatched (`--json` still prints the payload)

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
- **YAML header missing session.id**: exits 1 with the header path and base stderr detail
- **Newest header corrupt**: next-newest `ses_*/` dir is tried before the flat fallback
- **No state file**: still succeeds (reports "missing") unless `--state exists` (exits 2)
- **`--since` filters all sessions**: exits 1 with "could not find newest YAML log"
- **Symlinked log dir**: follows symlinks via `Path.rglob`

## Prohibited Actions

- Do NOT re-derive the sort or YAML extraction logic inline — always delegate to the base skill scripts.
- Do NOT hardcode log directory paths — use `.opencode/logs/` relative to repo root.

## Script Reference

`find-current-session.py`:

1. Resolves repo root via `$OPENCODE_REPO_ROOT` / `$AI_SUITE_ROOT`, git top-level, legacy `parents[4]` fallback (cached
   per-process via `lru_cache`)
2. Resolves base script paths under repo root (with `SCRIPT_DIR`-relative fallback)
3. Resolves log dir via `--log-dir`, `$OPENCODE_LOGS_DIR`, or `<repo-root>/.opencode/logs`
4. If `--dry-run`: emits discovery JSON and exits
5. Walks `ses_*/` dirs newest-first (filtered by `--since` if given), probes top 5 in parallel via `ThreadPoolExecutor`,
   accepting first header whose `session.id` parses
6. Runs `sort-by-mtime.py` on `.opencode/logs/` with glob `*.yaml` and `--limit 1`
7. Parses JSON Lines output to get the newest file path
8. Runs `extract-field.py` twice: once for `session.id`, once for `title`
9. Checks for `.opencode/logs/<sid>.state.json`
10. Applies `--state` gate (exit 2 on mismatch; `--json` still prints payload)
11. Prints results

## Composition by Lower-Level Skills

| Primitive | Composition Mechanism |
| ----------- | ---------------------- |
| `file-glob-sort-by-mtime` | `sort-by-mtime.py --dir .opencode/logs --glob *.yaml --limit 1` → newest path |
| `yaml-field-extract` | `extract-field.py --file <path> --key session.id` → session ID |

## Related Skills

- [`opencode-installed-plugin-lookup`](../opencode-installed-plugin-lookup/SKILL.md) — consumer of the logger-location
  convention (.opencode/logs/)
