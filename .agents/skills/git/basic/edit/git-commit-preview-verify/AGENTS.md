# Git Commit Preview Verify — Companion Bridge

## Purpose

Expose the preview-verification skill to non-skill-aware runtimes.
The operational SSOT lives in [SKILL.md](SKILL.md).

## When This Skill Applies

- Checking whether the titles in an existing preview appear in Git history.
- Verifying a completed atomic-commit batch before its retirement decision.
- Requesting optional cleanup after caller-owned completion and consent checks.

## Operational Procedure

Read [SKILL.md](SKILL.md) for the read-only default, optional cleanup
delegation, macOS Trash requirement, output/exit contracts, and regression
checks. Title matching does not replace the caller's content and plan-coverage audit.

## Cross-References

- [Atomic commit construction](../../../../git-atomic-commit-construction/SKILL.md) — preview producer and consumer.
- [Safe file cleanup](../../../../general/file/safe-file-cleanup/SKILL.md) — delegated removal primitive.
- [Commit metadata extraction](../../../../git-commit-metadata-extraction/SKILL.md) — individual commit inspection.
