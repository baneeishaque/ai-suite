# Changelog

All notable changes to the `vscode-active-window-editors` skill are documented
in this file.

Format: based on [Keep a Changelog](https://keepachangelog.com/), and this
project adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0] — 2026-08-12

### Added

- `--mode {all,files}` CLI flag (default `all`), passed through to the base
  extractor. `all` = every tab (file/webview/terminal) with `[type]` tags and
  `# group` markers; `files` = file-only projection.

### Changed

- SKILL.md v1.0.0 → v1.1.0 (CLI contract, stdout description, protocol, Edge
  Cases, Composition by Lower-Level Skills).
- AGENTS.md companion bridge refreshed for the complete-tab-bar behavior.

### Notes

- Enrichment ("List open VS Code editor tabs", 2026-08-12) — the base
  extractor now reports webview/terminal tabs by default; this composer
  forwards the `--mode` choice.

## [1.0.0] — 2026-08-11

### Added

- Initial extraction of the `vscode-active-window-editors` composer skill from
  the "Listing absolute paths of open VSCode files" workflow.
- `scripts/list-active-window-editors.py` — macOS discovery layer that
  resolves the active VS Code window's `state.vscdb` via workspaceStorage
  mtime sorting + `workspace.json` title cross-check, then delegates to
  the `vscode-state-vscdb-editor-extract` base script.
- SKILL.md — full skill documentation with CLI contract, protocol, and
  composition rationale.
- AGENTS.md — operational reminders and command reference.
- TRACEABILITY.md — lineage to the source logs and technical findings.

### Key design decisions

- Discovery is macOS-only (`sys.platform == "darwin"` guard, exits 2 on other
  platforms). Non-macOS users should use the base
  `vscode-state-vscdb-editor-extract` skill directly with `--db`.
- The base script is resolved via an **anchored relative path**
  (`../..` from `scripts/`), so it works regardless of `cwd`. The composer
  verifies the base exists and exits 2 with a clear error if missing.
- `CODE_APP_NAMES` priority order: `Code - Insiders` → `Code` →
  `VSCodium` → `Cursor` → `Code - Insiders Beta` → `Code - Exploration`.
