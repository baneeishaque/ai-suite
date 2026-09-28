# SWH Content Link Mint — Companion Bridge

This file is the bridge for non-skill-aware runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to mint citable Software Heritage content links from files in the local working tree.
- You need `;lines=` line references appended AFTER ingest confirmation.
- You are authoring documentation or commit messages that cite specific file versions.

## Operational Procedure

1. Ensure the origin + HEAD is archived (`swh-save-code-now` + `swh-ingest-verify`).
2. Run `mint-content-links.py` with `--origin <url>` and the file paths.
3. Add `--verify` to skip un-ingested blobs; add `--lines N-M` after confirmation.

## Cross-References

- [`SKILL.md`](SKILL.md) — full protocol, link grammar, `;lines=` gate.
- [`git-blob-hash`](../../general/file/git-blob-hash/SKILL.md) — base skill providing the blob hash.
- [`content-ingestion-check`](../../general/file/content-ingestion-check/SKILL.md) — base skill providing the ingest gate.
- [`swh-save-code-now`](../../software-heritage/save-code-now/SKILL.md) — run before minting to force an archive visit.
- [`swh-ingest-verify`](../../software-heritage/ingest-verify/SKILL.md) — confirm the revision is snapshotted.