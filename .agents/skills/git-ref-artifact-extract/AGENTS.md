# Git Ref Artifact Extract — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes that auto-load `AGENTS.md` by filename convention. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to capture a file exactly as it exists at a git ref (HEAD, branch, tag, or stash commit) for comparison, audit, or diffing against another version.
- You need the confirmed git-ref scratch naming `<purpose>_<ref-slug>_<full-sha>` under `<repo>/scratch/<session-id>/`.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full CLI contract, protocol, and edge cases. Do NOT execute any step without first loading `SKILL.md`.

## Key Rules

1. Run `extract-ref-artifact.py --repo <repo> --ref <rev> --path <file> --purpose <slug>`.
2. Ref captures carry the full SHA — never a timestamp.
3. The output path always lives under `<repo>/scratch/<session-id>/`.

## Cross-References

- [`scratch-artifact-naming`](../general/file/scratch-artifact-naming/SKILL.md) — delegated for path + naming
- [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md) — the capture doctrine for the same scratch tree
