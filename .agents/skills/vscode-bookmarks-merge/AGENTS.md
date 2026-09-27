# VS Code Bookmarks Merge — Companion Bridge

## Purpose

This file is a companion bridge for non-skill-aware agent runtimes. The
operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

You have two `.vscode/bookmarks.json` files and need to merge them — combine
bookmarks by file path, deduplicate by (line, column), and sort. The skill
handles the structural JSON merge only; it does not remap paths.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
the CLI contract, merge algorithm, and verification steps. Do NOT execute
any step without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`json-deep-sort`](../json-deep-sort/SKILL.md) — deep JSON sorting
  utility.
- [`vscode-bookmarks-cross-repo-migrate`](../vscode-bookmarks-cross-repo-migrate/SKILL.md) —
  composer that handles cross-repo path remapping and invokes this base skill.
- Skill Factory [`SKILL.md`](../skill-factory/SKILL.md) —
  creation protocol for skills like this one.
