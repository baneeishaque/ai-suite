# Changelog — vscode-state-vscdb-editor-extract

All notable changes to this skill are documented here. See
[`SKILL.md`](SKILL.md) for the operational SSOT.

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

- Enrichment session `00dd58393ffertAuAtxH2qg1EU` ("List open VS Code editor
  tabs", 2026-08-12): the file-only projection silently dropped webview and
  terminal tabs, so it never matched the on-screen tab bar; the webview source
  file was found to be recoverable via `value['state']['resource']`.

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

- Extracted from session `02f0d4351ffeTl1vcyqbPXZqvW` ("Listing absolute paths
  of open VSCode files", 2026-08-05), turns 002–003.
- The `sticky: N` count is the only pinned signal — VS Code does not serialize
  a per-editor `pinned` flag in `serializedGrid`.
- The `memento/workbench.editors.files.textFileEditor` key was identified as
  an unreliable source (it stores view-state history including closed tabs)
  and is explicitly documented as an anti-pattern in SKILL.md §Anti-Patterns.
