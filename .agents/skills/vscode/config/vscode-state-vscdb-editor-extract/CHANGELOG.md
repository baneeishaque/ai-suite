# Changelog — vscode-state-vscdb-editor-extract

All notable changes to this skill are documented here. See
[`SKILL.md`](SKILL.md) for the operational SSOT.

## [1.3.0] — 2026-10-30

### Added

- File records now expose `scheme`, `external`, `authority`, and `uri`
  (additive JSON fields). A `fileEditorInput` may be an extension virtual
  document whose `path` is a URI path (e.g. `gist://<gist-id>/<name>`), not a
  local absolute path.
- Text mode (`--mode all`) renders non-`file` schemes via their `external` URI;
  `--mode files` emits them as `#non-file: <uri>` markers instead of misusing
  the URI path as an fsPath.

### Changed

- SKILL.md v1.2.0 → v1.3.0 (Description, CLI contract, JSON schema, Protocol,
  Script Reference, Edge Cases, Anti-Patterns).

## [1.2.0] — 2026-10-14

### Fixed

- Off-by-one in the pinned derivation. VS Code's group-level `sticky` is the
  **inclusive array index of the LAST pinned editor**, not a count — verified
  against `EditorGroupModel.isSticky()` (`index <= this.sticky`, field
  initialized to `-1`, serialized as `sticky: r >= 0 ? r : undefined`). The
  script previously used `pinned = index < sticky` and defaulted a missing
  `sticky` to `0`, which dropped the final pinned tab and wrongly pinned index 0
  of pinned-free groups. Now `pinned = index <= sticky` with `sticky` defaulting
  to `-1`.
- `group_sticky` in JSON output now carries the same last-pinned-index value.

### Changed

- SKILL.md v1.1.0 → v1.2.0 (sticky semantics in Description, JSON example,
  Protocol, Script Reference, and a new Anti-Patterns row for the count
  misreading).

## [1.1.0] — 2026-08-12

### Added

- `--mode {all,files}` CLI flag (default `all`). Text output now lists EVERY
  tab — file, webview/markdown-preview, terminal — in tab-bar order with a
  `[type]` tag, `# group <id>` split-view markers, and `[pinned]` annotation.
  `--mode files` preserves the legacy file-only projection byte-for-byte.
- Webview source-path resolution: `extract_webview_source_path()` parses the
  webview editor's `value['state']` (JSON-encoded string) and resolves its
  `resource` key — a URI dict (`path`/`fsPath`) or a `file://` string — plus
  top-level fallbacks. Markdown-preview / custom-editor backing files are now
  first-class tabs.
- Per-editor `type` (`file` / `webview` / `terminal` / `other`), `label`, and
  `source_path` fields in JSON output (additive; existing fields unchanged).

### Changed

- SKILL.md v1.0.0 → v1.1.0 (CLI contract, output examples, Edge Cases,
  Anti-Patterns, Script Reference).
- AGENTS.md companion bridge refreshed for the complete-tab-bar behavior.

### Notes

- Enrichment ("List open VS Code editor tabs", 2026-08-12): the file-only
  projection silently dropped webview and terminal tabs, so it never matched
  the on-screen tab bar; the webview source file was found to be recoverable
  via `value['state']['resource']`.

## [1.0.0] — 2026-08-11

### Added

- Initial creation of the `vscode-state-vscdb-editor-extract` base skill.
- `scripts/extract-editors.py`: Tier-1 Python script that reads a VS Code
  `state.vscdb` SQLite database, parses the `memento/workbench.parts.editor`
  memento key, walks the `editorpart.state.serializedGrid` grid tree, and
  emits open editor file paths in display (tab-bar) order with pinned
  annotation derived from the group-level `sticky` count.
- SKILL.md, AGENTS.md (companion bridge), and this changelog.

### Notes

- Extracted from the "Listing absolute paths of open VSCode files"
  workflow (2026-08-05).
- The `sticky: N` count is the only pinned signal — VS Code does not serialize
  a per-editor `pinned` flag in `serializedGrid`.
- The `memento/workbench.editors.files.textFileEditor` key was identified as
  an unreliable source (it stores view-state history including closed tabs)
  and is explicitly documented as an anti-pattern in SKILL.md §Anti-Patterns.
