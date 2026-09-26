# OpenCode Session Path Attribution — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to answer "which session touched path X, when, with what exact
  command" by sweeping opencode logger per-turn session logs
- A higher-level workflow (e.g. the git-commit-dangling-link-audit drift
  gate) needs an evidence card attributing a moved/uncommitted path to its
  session

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including
the CLI contract, exit codes, and the matching semantics. Do NOT execute
any step without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`opencode-session-yaml-tool-call-extractor`](../opencode-session-yaml-tool-call-extractor/SKILL.md)
  — consumed base: per-turn-file subprocess provider of stdout JSONL
- [`opencode-installed-plugin-lookup`](../opencode-installed-plugin-lookup/SKILL.md)
  — consumed base: locates the logger plugin and its logs convention
- [`opencode-current-session-id`](../opencode-current-session-id/SKILL.md)
  — sibling in the `opencode/` group: active-session resolution
- [`git-commit-dangling-link-audit`](../../git-commit-dangling-link-audit/SKILL.md)
  — composer: drift gate invokes this skill for evidence cards
