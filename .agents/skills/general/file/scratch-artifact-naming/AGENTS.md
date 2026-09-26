# Scratch Artifact Naming — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes that auto-load `AGENTS.md` by filename convention. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are about to capture command output, probe results, or git-ref content into a repo's `scratch/` folder and need the correct session-scoped path and naming.
- You need the current opencode session ID as the scratch subfolder name.
- You are authoring or enriching a skill that writes artifacts under `<repo>/scratch/`.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full CLI contract, naming variants, and edge cases. Do NOT execute any step without first loading `SKILL.md`.

## Key Rules

1. Always place artifacts at `<repo>/scratch/<session-id>/` — never at the scratch root, never in `/tmp`.
2. Timestamp variant: `<purpose>_<YYYY-MM-DD_HH-MM-SS>`; git-ref variant: `<purpose>_<ref-slug>_<full-sha>`. Do not mix.
3. Run the script for the stem path; append the extension yourself.

## Cross-References

- [`opencode-current-session-id`](../../opencode/opencode-current-session-id/SKILL.md) — composed for auto session-ID discovery
- [`repo-scratch-output-capture`](../../../repo-scratch-output-capture/SKILL.md) — sibling; owns `.out`/`.err` pairing and the gitignore guarantee
- [`git-ref-artifact-extract`](../../../git-ref-artifact-extract/SKILL.md) — composer that delegates naming to this skill
