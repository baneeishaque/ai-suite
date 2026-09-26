# Git Commit Dangling-Link Audit — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are about to finalize a commit that moves/reorders paths, and need
  to verify every markdown relative link survives in the committed tree
- A link target is missing from BOTH the working tree and the git index,
  and you need evidence of which session moved the path

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full protocol (scope gate, preview
sweep, drift gate, decision gate, prompt gate, verify gate) and the CLI
contract of `scripts/detect-dangling-links.py`. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally
non-actionable.

## Cross-References

- [`opencode-session-path-attribution`](../opencode/opencode-session-path-attribution/SKILL.md)
  — drift-gate evidence provider
- [`opencode-installed-plugin-lookup`](../opencode/opencode-installed-plugin-lookup/SKILL.md)
  — transitive: logger location for attribution
- [`deleted-files-audit`](../deleted-files-audit/SKILL.md) —
  complementary audit
- [`gitignored-reference-detection`](../gitignored-reference-detection/SKILL.md)
  — sibling audit
