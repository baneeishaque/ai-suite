# VS Code Active Window Editors — Companion Bridge

## Purpose

This file is a bridge for non-skill-aware agent runtimes that auto-load
`AGENTS.md` by filename convention. The operational single source of truth
lives in [`SKILL.md`](SKILL.md). Read that file for the full procedure,
including all mandates, scripts, and verification steps. Do NOT execute any
step without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## When This Skill Applies

Apply this composer skill when you are on macOS and need what is open in the
editor tabs of the **active** VS Code window — files, webview/markdown-preview
sources, and terminals — in tab-bar (pinned-first) order, and you do NOT know
the `state.vscdb` path ahead of time (so you need automatic discovery of the
active window). Default output (`--mode all`) lists every tab with a `[type]`
tag and `# group` markers; `--mode files` gives the file-only projection.

If you already know the `state.vscdb` path, use the base
[`vscode-state-vscdb-editor-extract`](../vscode-state-vscdb-editor-extract/SKILL.md)
directly instead.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full protocol: CLI contract, script
reference, discovery logic, and edge cases. Do NOT execute any step without
first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`vscode-state-vscdb-editor-extract`](../vscode-state-vscdb-editor-extract/SKILL.md) —
  base skill that parses the `state.vscdb` SQLite database; this composer
  discovers the active window's DB path on macOS and delegates to it
- [`vscode-state-vscdb-merge`](../../../vscode-state-vscdb-merge/SKILL.md) —
  compares/merges `state.vscdb` across Git refs (complementary; not composed)

- [`skill-factory`](../../../skill-factory/SKILL.md) — governs the companion-bridge
  template that this file follows (§2.3)
