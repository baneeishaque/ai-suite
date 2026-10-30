# Traceability — vscode-state-vscdb-editor-extract

## Enrichment

### 2026-10-30

- **Trigger:** a user asked for "complete absolute paths" after a tab list
  rendered `gist://` virtual documents as bare `/name` paths that looked like
  local absolute paths.
- **Key finding:** extension virtual documents serialize as ordinary
  `fileEditorInput` entries (`resourceJSON.scheme = "gist"`,
  `authority = <gist-id>`, `external = gist://<gist-id>/<name>`); their `path`
  is a URI path, not an absolute filesystem path. File records now expose
  `scheme` / `external` / `authority` / `uri`; text mode uses the external URI
  for non-`file` schemes, and `--mode files` marks them `#non-file:`.

### 2026-10-14

- **Trigger:** a user pinned-marked markdown-preview tab (array index equal to
  the group's `sticky` value) was reported as unpinned — VS Code showed every
  tab in the group as pinned.
- **Key finding:** the group-level `sticky` is the **inclusive index of the last
  pinned editor**, not a count. Confirmed by reading VS Code Insiders'
  `workbench.desktop.main.js`: `EditorGroupModel.isSticky(index)` returns
  `index <= this.sticky`, the field is initialized to `-1`, and `serialize()`
  emits `sticky: r >= 0 ? r : undefined` (so absent ⇒ no pinned editors). The
  script's `pinned = index < sticky` was off by one and defaulted absent to `0`.
  Fixed to `pinned = index <= sticky` with `sticky` defaulting to `-1`.

### 2026-08-12

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

## Source

- **Source workflow:** "Listing absolute paths of open VSCode files"
- **Date:** 2026-08-05
- **Log files:**
    - `<workspace-root>/.opencode/logs/<session-id>/002-2026-08-05T08-17-58-407Z.yaml`
    (investigation loop — DB discovery, rejected JXA accessibility path,
    workspaceStorage mtime heuristic)
    - `<workspace-root>/.opencode/logs/<session-id>/003-2026-08-05T08-19-33-346Z.yaml`
    (pinned ordering — `sticky: 32` discovery, `editors[]` display-order
    verification, tab enumeration)

## Key Technical Findings

1. The live editor tab state lives in the **running window's** workspace
   storage: `state.vscdb` → key `memento/workbench.parts.editor` →
   `editorpart.state.serializedGrid`.
2. Each leaf node's `editors[]` array is in **tab-display order** (pinned block
   first).
3. `sticky: N` at the group level is the **inclusive array index of the LAST
   pinned (sticky) tab** — pinned iff `index <= N`; absent when nothing is
   pinned. The pinned flag is **not** serialized per editor — `sticky` is the
   only signal. (Corrected 2026-10-14 from the original "count" reading; see
   Enrichment below.)
4. `mru: [...]` is most-recently-used order (different axis from display order).
5. `memento/workbench.editors.files.textFileEditor` stores **view-state
   history** (includes closed tabs) — NOT a reliable source for currently-open
   tabs. Rejected path.
6. JXA/System Events accessibility-tree walks were attempted but Electron web
   content was not exposed. Rejected path.
7. The correct workspaceStorage entry is identified by **mtime** (newest =
   active window), confirmed via `workspace.json` folder/workspace field.

## Skill Origin

- **Created by:** Base skill extracted from the source workflow.
- **Skill Factory:** 2026-08-11.
