# VS Code Bookmarks Cross-Repo Migration — Companion Bridge

## Purpose

This file is a companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Files have moved from one repository to another, and the VS Code bookmarks
in `.vscode/bookmarks.json` need updating — the old bookmarks point to paths
that no longer exist. This skill discovers the new paths, merges the
bookmarks into the target repo's bookmark file, and optionally cleans up
the source.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
the path remapping strategy, CLI contract, and verification steps. Do NOT
execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [`vscode-bookmarks-merge`](../vscode-bookmarks-merge/SKILL.md) — base skill
  that handles the actual JSON merge, deduplication, and sorting.
- Skill Factory [`SKILL.md`](../skill-factory/SKILL.md) — creation protocol.
