# AGENTS.md Recovery from Session — Composer Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes
that auto-load `AGENTS.md` by filename convention. The operational SSOT
lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- AGENTS.md was accidentally overwritten or lost via
  `git checkout HEAD -- AGENTS.md`
- A session export exists with the lost content in git diff format
- Need to restore skills table entries and their accompanying file
  structure

## Operational Procedure

Load [`SKILL.md`](SKILL.md) for the complete recovery workflow:

1. Extract AGENTS.md diff from session
2. Apply diff to working copy
3. Verify alphabetical order
4. Fix markdownlint errors
5. Commit changes

## Cross-References

- [`opencode-session-diff-extractor`](../opencode-session-diff-extractor/SKILL.md) —
  Base primitive that does the extraction work
- [`skill-library-domain-grouping`](../general/skill-library-domain-grouping/SKILL.md) —
  Rule set for placing new skills alphabetically in the skills table
- [`text-lines-sort-by-length`](../text-lines-sort-by-length/SKILL.md) —
  Optional helper for reordering out-of-order skills tables
