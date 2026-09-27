# Traceability — vscode-state-vscdb-editor-extract

## Enrichment Session

- **Session ID:** `00dd58393ffertAuAtxH2qg1EU`
- **Session title:** "List open VS Code editor tabs"
- **Session date:** 2026-08-12
- **Trigger:** user's on-screen VS Code tab bar contained terminal and webview
  tabs that the v1.0.0 file-only projection did not report — the output never
  matched the visual tab bar.
- **Key finding 1:** webview tabs (`workbench.editors.webviewEditor`) carry no
  top-level `resourceJSON`/`resource`; their backing source file lives in
  `value['state']` — a JSON-encoded string whose parsed object has a
  `resource` key (URI dict `path`/`fsPath`, or a `file://` URI string).
  `extract_webview_source_path()` now resolves all three shapes.
- **Key finding 2:** the file-only projection is structurally incapable of
  matching the tab bar when terminals/webviews are present; the default
  `--mode all` output (every tab + `[type]` tags + `# group` markers) is the
  faithful view. `--mode files` retains the legacy projection for callers that
  only want source files.
- **Plan artifact:**
  `<workspace-root>/docs/2026-08-12_00dd58393ffertAuAtxH2qg1EU_list-open-vs-code-editor-tabs_implementation-plan_v1.md`

## Source Session

- **Session ID:** `02f0d4351ffeTl1vcyqbPXZqvW`
- **Session title:** "Listing absolute paths of open VSCode files"
- **Session date:** 2026-08-05
- **Log files:**
    - `<workspace-root>/.opencode/logs/ses_02f0d4351ffeTl1vcyqbPXZqvW/002-2026-08-05T08-17-58-407Z.yaml`
    (investigation loop — DB discovery, rejected JXA accessibility path,
    workspaceStorage mtime heuristic)
    - `<workspace-root>/.opencode/logs/ses_02f0d4351ffeTl1vcyqbPXZqvW/003-2026-08-05T08-19-33-346Z.yaml`
    (pinned ordering — `sticky: 32` discovery, `editors[]` display-order
    verification, tab enumeration)

## Key Technical Findings (verbatim from session logs)

1. The live editor tab state lives in the **running window's** workspace
   storage: `state.vscdb` → key `memento/workbench.parts.editor` →
   `editorpart.state.serializedGrid`.
2. Each leaf node's `editors[]` array is in **tab-display order** (pinned block
   first).
3. `sticky: N` at the group level = number of pinned (sticky) tabs. The pinned
   flag is **not** serialized per editor — `sticky` count is the only signal.
4. `mru: [...]` is most-recently-used order (different axis from display order).
5. `memento/workbench.editors.files.textFileEditor` stores **view-state
   history** (includes closed tabs) — NOT a reliable source for currently-open
   tabs. Rejected path.
6. JXA/System Events accessibility-tree walks were attempted but Electron web
   content was not exposed. Rejected path.
7. The correct workspaceStorage entry is identified by **mtime** (newest =
   active window), confirmed via `workspace.json` folder/workspace field.

## Skill Origin

- **Created by:** Base skill extracted from session `02f0d4351ffeTl1vcyqbPXZqvW`.
- **Skill Factory session:** `011fd359dffe2p11kHfOQFbMaZ` (2026-08-11) — "VSCode
  open editor tabs pin order skill".
- **Plan artifact:**
  `<workspace-root>/docs/implementation-plans/2026-08-11_011fd359dffe2p11kHfOQFbMaZ_vscode-open-editor-tabs-pin-order-skill_implementation-plan_v1.md`
