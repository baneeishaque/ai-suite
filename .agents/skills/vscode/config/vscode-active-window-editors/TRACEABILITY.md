# Traceability — vscode-active-window-editors

## Enrichment Session

- **Session ID:** `00dd58393ffertAuAtxH2qg1EU`
- **Session title:** "List open VS Code editor tabs"
- **Session date:** 2026-08-12
- **Change:** added `--mode {all,files}` passthrough to the base extractor so
  the composer can request either the complete tab list (all) or the
  file-only projection (files). Default `all` — matching the base skill v1.1.0.
- **Plan artifact:**
  `<workspace-root>/docs/2026-08-12_00dd58393ffertAuAtxH2qg1EU_list-open-vs-code-editor-tabs_implementation-plan_v1.md`

## Purpose

This composer skill extracts the **discovery** half of the workflow from
session `02f0d4351ffeTl1vcyqbPXZqvW` ("Listing absolute paths of open VSCode
files") into a reusable, macOS-specific skill. The **parsing** half lives in
the base skill [`vscode-state-vscdb-editor-extract`](../vscode-state-vscdb-editor-extract/TRACEABILITY.md).

## Source Session

| Field | Value |
| --- | --- |
| Session ID | `02f0d4351ffeTl1vcyqbPXZqvW` |
| Session title | Listing absolute paths of open VSCode files |
| Session date | 2026-08-05 |
| Log path | `<workspace-root>/.opencode/logs/ses_02f0d4351ffeTl1vcyqbPXZqvW/` |

## Log Turn Attribution

| Log turn | Technique documented |
| --- | --- |
| 001 | Initial ask: list absolute paths of open VS Code files. |
| 002 | Investigation (16 tool calls): explored DB discovery, tried and rejected JXA/System Events accessibility-tree approach; confirmed workspaceStorage mtime heuristic as the active-window selector; read `workspace.json` to match workspace folder URI. |
| 003 | Pinned ordering (5 tool calls): confirmed `sticky: N` group-level integer is the pinned signal; `editors[]` array is in tab-display order; `mru` is a separate axis; `memento/workbench.editors.files.textFileEditor` rejected (view-state history, includes closed tabs). |
| 004 | Delivered final editor path list; invoked `opencode-current-session-id` skill; confirmed the mtime-based window discovery. |

## Skill Decomposition

| Workflow step | Source turn | Skill |
| --- | --- | --- |
| Find Code-family workspaceStorage dir | 002 | composer (`vscode-active-window-editors`) |
| Sort by mtime → active window | 002 | composer (`vscode-active-window-editors`) |
| Read workspace.json for title match | 002 | composer (`vscode-active-window-editors`) |
| Resolve `<hash>/state.vscdb` | 002 | composer (`vscode-active-window-editors`) |
| SQLite query → memento key | 002 | base (`vscode-state-vscdb-editor-extract`) |
| Parse serializedGrid tree | 003 | base (`vscode-state-vscdb-editor-extract`) |
| Extract fileEditorInput path | 003 | base (`vscode-state-vscdb-editor-extract`) |
| Annotate pinned via `sticky: N` | 003 | base (`vscode-state-vscdb-editor-extract`) |

## Redaction

- All paths in this skill's authored docs and scripts are redacted to
  canonical placeholders (`<user-home>`, `<workspace-root>`) or resolved
  dynamically via `os.path.expanduser("~")` / `__file__` anchoring.
- The specific workspace hash
  `d26f622cd355b87916af87213b4501b9` is referenced only as an example in
  TRACEABILITY.md — not hardcoded in any script.
