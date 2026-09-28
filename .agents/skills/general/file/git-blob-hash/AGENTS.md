# Git Blob Hash — Companion Bridge

This file is the bridge for non-skill-aware runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to compute the git blob SHA-1 of a file (identical to `git hash-object` output).
- You need a SWH `cnt` identifier from local file content without invoking git.
- You need to verify a file's content matches a known hash.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational protocol before invoking [`scripts/compute-blob-sha1.py`](scripts/compute-blob-sha1.py). Do NOT execute without first loading the skill.

## Cross-References

- [`swh-content-link-mint`](../../../software-heritage/content-link-mint/SKILL.md) — composer that delegates blob hashing to this base skill.
- [`content-ingestion-check`](../content-ingestion-check/SKILL.md) — base skill for checking whether a blob hash is archived in a content-addressable store.
