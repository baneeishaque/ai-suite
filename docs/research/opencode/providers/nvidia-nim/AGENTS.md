# NVIDIA NIM Provider Research

## Purpose

Own current NVIDIA NIM API/catalog research and OpenCode's cache-aware supplemental configuration.

## Ownership

- [README.md](README.md) is the entry point and dated integration summary.
- [cache-and-supplement.md](cache-and-supplement.md) owns exact-ID source layers and non-overlap rules.
- [api-contracts-and-limits.md](api-contracts-and-limits.md) owns hosted endpoints, limits, and special-purpose APIs.
- [refresh-and-verify.md](refresh-and-verify.md) owns operational refresh/apply/verification guidance.
- [sources-and-open-questions.md](sources-and-open-questions.md) owns source provenance and unresolved capabilities.
- [evidence/README.md](evidence/README.md) owns portable machine-readable datasets and byte hashes.
- Runtime source/configuration remains owned by the configuration repository's OpenCode contracts.

## Local Contracts

- Inherit the [root contract](../../../../../AGENTS.md) and [documentation contract](../../../../AGENTS.md).
- Supplement only exact NVIDIA IDs absent from the current `cache.nvidia.models` set.
- Do not overwrite cached models, refresh/edit the cache to hide a difference, or change unrelated providers/auth.
- Distinguish key discovery, public catalog pages, endpoint schemas, local cache, effective runtime, and inference results.
- An API-shaped classifier or embedding endpoint is not general assistant-chat support.
- Preserve source-provided names/IDs; omit unknown prices/limits and keep unsupported/unresolved entries in evidence.
- No credentials, account identifiers, session IDs, local scratch paths, or fabricated live-test claims in durable docs.

## Work Guidance

- Prefer the hosted endpoint contract over upstream vendor maximum context when they differ.
- Retire only unchanged generated supplement entries that are now cached, using explicit ownership evidence.
- Preserve pre-existing user overrides and stop on managed-entry drift; do not silently replace user work.
- Record catalog/schema verification separately from inference availability or free-access qualification.

## Verification

- Require exact runtime baseline-plus-supplement equality and zero generated cache overlap.
- Verify cache/auth hashes, non-NVIDIA config preservation, manifest hashes, and relative Markdown links.
- Run the sync tool's offline tests and standalone repository-root Markdown lint.

## Child DOX Index

- [evidence/README.md](evidence/README.md) indexes the portable supporting evidence.
