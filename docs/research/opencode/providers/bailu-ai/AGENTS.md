# Bailu AI Provider Research Contract

## Purpose

Own evidence-backed Bailu model-catalog, access/free-policy, OpenCode compatibility, and input-length research.

## Ownership

- [README.md](README.md) is the entry point and reading-order map.
- [catalog-layers.md](catalog-layers.md) owns exact-ID/count/source semantics.
- [access-and-model-classes.md](access-and-model-classes.md) owns availability, access, native classes, and errors.
- [free-model-and-billing-policy.md](free-model-and-billing-policy.md) owns verified-free labels, funding, and visibility.
- [input-data-length-and-workspace-context.md](input-data-length-and-workspace-context.md) owns client-only context limits.
- [implementation-history.md](implementation-history.md) owns actual source/configuration/probe evolution.
- [sources.md](sources.md) owns primary citations and dated qualifications.
- [open-questions.md](open-questions.md) owns unresolved facts and closure criteria.
- [evidence/README.md](evidence/README.md) owns portable datasets, hashes, and verification.
- Runtime config/generator source remains owned by the configuration repository's OpenCode contracts.

## Local Contracts

- Inherit the [root contract](../../../../../AGENTS.md) and [documentation contract](../../../../AGENTS.md).
- Preserve exact model IDs; separate configured, key-advertised, platform-published, blacklisted, and visible sets.
- Separate official claims, actual responses, current observations, historical snapshots, and unresolved facts.
- A free label requires verified zero-monetary access; a missing/zero cost estimate is not free evidence.
- Use an API-provided name or exact ID, with one confirmed-free annotation. Never generate names.
- Exclude payment-required, non-chat, blocked/down/improper, and unverified required client cases from visibility.
- Do not include secrets, cookies, credential fragments, session IDs, or local scratch/backup references.

## Work Guidance

- Explain input character/body limits separately from token-window limits.
- For client-only input-length failures, preserve the original result and retry the same case in a blank workspace.
- Record repo/global context controls separately from direct API results; a blank folder alone may retain global skills.
- Keep complete per-model dispositions and source-qualified limitations. Do not promote a prompt echo or empty HTTP 200.

## Verification

- Validate CSV row/unique-ID counts, exact set relationships, manifest hashes, and secret scans.
- Run standalone Markdown lint from the repository root and verify all relative links.

## Child DOX Index

- [evidence/README.md](evidence/README.md) owns the evidence inventory; no narrower contract is required.
