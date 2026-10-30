# Traceability — vscode-active-window-editors

## Enrichment

- **Date:** 2026-10-30
- **Change:** documented non-`file` URI schemes surfaced by base extractor
  v1.3.0. Extension virtual documents (e.g. `gist://<gist-id>/<name>`) reuse
  the file-editor shape; their `fs_path` is a URI path, so complete-path
  requests must report the JSON `uri`/`external` field, and `--mode files`
  marks them `#non-file:`.

- **Date:** 2026-10-14
- **Change:** inherited the base extractor's corrected pinned semantics (base
  v1.2.0) — the group-level `sticky` value is the inclusive last-pinned index,
  so `pinned = index <= sticky` (absent ⇒ none). No script change in this
  composer; the `[pinned]` annotation it forwards is now correct.

- **Date:** 2026-08-12
- **Change:** added `--mode {all,files}` passthrough to the base extractor so
  the composer can request either the complete tab list (all) or the
  file-only projection (files). Default `all` — matching the base skill v1.1.0.

## Purpose

This composer skill extracts the **discovery** half of the "Listing absolute paths of open VSCode files"
workflow into a reusable, macOS-specific skill. The **parsing** half lives in the base skill
[`vscode-state-vscdb-editor-extract`](../vscode-state-vscdb-editor-extract/TRACEABILITY.md).

## Source

| Field | Value |
| --- | --- |
| Source workflow | Listing absolute paths of open VSCode files |
| Date | 2026-08-05 |
| Log path | `<workspace-root>/.opencode/logs/<session-id>/` |

## Investigation Notes

| Technique documented |
| --- |
| Initial ask: list absolute paths of open VS Code files. |
| Investigation (16 tool calls): explored DB discovery, tried and rejected JXA/System Events accessibility-tree approach; confirmed workspaceStorage mtime heuristic as the active-window selector; read `workspace.json` to match workspace folder URI. |
| Pinned ordering (5 tool calls): confirmed `sticky: N` group-level integer is the pinned signal; `editors[]` array is in tab-display order; `mru` is a separate axis; `memento/workbench.editors.files.textFileEditor` rejected (view-state history, includes closed tabs). |
| Delivered final editor path list; invoked `opencode-current-session-id` skill; confirmed the mtime-based window discovery. |

## Skill Decomposition

| Workflow step | Skill |
| --- | --- |
| Find Code-family workspaceStorage dir | composer (`vscode-active-window-editors`) |
| Sort by mtime → active window | composer (`vscode-active-window-editors`) |
| Read workspace.json for title match | composer (`vscode-active-window-editors`) |
| Resolve `<hash>/state.vscdb` | composer (`vscode-active-window-editors`) |
| SQLite query → memento key | base (`vscode-state-vscdb-editor-extract`) |
| Parse serializedGrid tree | base (`vscode-state-vscdb-editor-extract`) |
| Extract fileEditorInput path | base (`vscode-state-vscdb-editor-extract`) |
| Annotate pinned via `sticky: N` (last-pinned index) | base (`vscode-state-vscdb-editor-extract`) |

## Redaction

- All paths in this skill's authored docs and scripts are redacted to
  canonical placeholders (`<user-home>`, `<workspace-root>`) or resolved
  dynamically via `os.path.expanduser("~")` / `__file__` anchoring.
- Workspace-specific hashes are never hardcoded in scripts; discovery resolves the active window's paths
  dynamically at runtime.
