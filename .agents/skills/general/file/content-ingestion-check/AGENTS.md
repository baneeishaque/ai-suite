# Content Ingestion Check — Companion Bridge

This file is the bridge for non-skill-aware runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to check whether a git blob SHA-1 is already archived in a content-addressable store.
- You need to verify content ingestion status before emitting citation links.
- You need a generic "is this hash known here?" HTTP primitive for any archive with a hash-lookup API.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full protocol before invoking [`scripts/check-ingestion.py`](scripts/check-ingestion.py). Do NOT execute without first loading the skill.

## Cross-References

- [`git-blob-hash`](../git-blob-hash/SKILL.md) — base skill that computes the git blob SHA-1 from local file content (typically called first).
- [`swh-content-link-mint`](../../../software-heritage/content-link-mint/SKILL.md) — composer that delegates ingestion verification to `check-ingestion.py` to enforce the ";lines= only after ingest" gate.
