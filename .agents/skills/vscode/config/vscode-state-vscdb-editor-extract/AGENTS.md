# VS Code state.vscdb Editor Extract — Companion Bridge

## Purpose

This file is a bridge for non-skill-aware agent runtimes that auto-load
`AGENTS.md` by filename convention. The operational single source of truth
lives in [`SKILL.md`](SKILL.md). Read that file for the full procedure,
including all mandates, scripts, and verification steps. Do NOT execute any
step without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## When This Skill Applies

Apply this base skill when you have a VS Code `state.vscdb` SQLite database and
need to extract what is currently open in editor tabs — files, webview /
markdown-preview sources, and terminals — in display (tab-bar) order, with
pinned (sticky) annotation and split-view group markers. The parser reads the
`memento/workbench.parts.editor` key → `editorpart.state.serializedGrid` and
walks the grid tree to leaf editor groups. Default text output (`--mode all`)
lists every tab with a `[type]` tag; `--mode files` emits the file-only
projection.

If you do **not** know the `state.vscdb` path and need macOS active-window
discovery, use the composer [`vscode-active-window-editors`](../vscode-active-window-editors/SKILL.md)
instead.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full protocol: CLI contract, script
reference, edge cases, and anti-patterns. Do NOT execute any step without first
loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`vscode-active-window-editors`](../vscode-active-window-editors/SKILL.md) —
  composer that discovers the active window's `state.vscdb` on macOS and
  delegates to this base skill
- [`vscode-state-vscdb-merge`](../../../vscode-state-vscdb-merge/SKILL.md) —
  compares/merges `state.vscdb` across Git refs (complementary, not a
  replacement)
