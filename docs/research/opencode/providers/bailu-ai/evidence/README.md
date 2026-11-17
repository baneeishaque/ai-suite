<!-- title: Bailu portable machine-readable audit evidence -->

# Portable Evidence

| File | Meaning |
| --- | --- |
| [model-inventory.csv](model-inventory.csv) | One row per exact ID, source membership, declared metadata, and observation scope. |
| [model-policy.csv](model-policy.csv) | Complete derived free/compatibility/blacklist/name decisions. |
| [direct-api-probe-results.csv](direct-api-probe-results.csv) | Every current direct/classification attempt and complete per-model outcome. |
| [opencode-probe-results.csv](opencode-probe-results.csv) | Typed assistant/read-tool checks, context controls, isolated/saved distinctions, and actual outcomes. |
| [input-length-retry-summary.json](input-length-retry-summary.json) | Whether the conditional retry occurred and its measured/unknown limit qualifications. |
| [provider-payload-free-only.jsonc](provider-payload-free-only.jsonc) | Reviewed credential-free provider metadata and exact blacklist. |
| [catalog-reconciliation-summary.json](catalog-reconciliation-summary.json) | Set/count equality, final model IDs, applied hash/preservation/meter scope. |
| [manifest.json](manifest.json) | Relative paths, SHA-256, rows, timestamps, and methodology. |

## Verification

Check every CSV's row/unique-ID count and its relationship to the 60-ID universe.
Prove visible/blacklist sets are disjoint and cover every retained definition; compare a fresh runtime listing.
Validate manifest hashes, complete required client events/results, free-label idempotency,
and no secret/session/local-path leakage.
Missing/failed/pending evidence is a qualification, not a zero-cost or successful-call default.
