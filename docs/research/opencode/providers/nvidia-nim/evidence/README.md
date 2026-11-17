<!-- title: NVIDIA NIM cache reconciliation portable evidence -->

# Portable Evidence

| File | Contract |
| --- | --- |
| [api-models.json](api-models.json) | All 32 exact authenticated discovery rows; no key. |
| [cache-model-ids.json](cache-model-ids.json) | All 52 cached IDs, observation date, and source cache hash. |
| [missing-model-metadata.json](missing-model-metadata.json) | All 16 missing IDs, source names/URLs/statuses, schema limits, and dispositions. |
| [provider-supplement.jsonc](provider-supplement.jsonc) | The four generated definitions, with no cached-ID copies or credentials. |
| [supplement-ownership.json](supplement-ownership.json) | Portable mirror of persistent managed definitions and skipped-ID reasons. |
| [reconciliation.json](reconciliation.json) | Exact baseline/runtime union, zero overlap, preservation proofs, and no-inference qualification. |
| [manifest.json](manifest.json) | Byte sizes, SHA-256, source time/method, and successful secret/local-reference scan. |

## Checks

- Require 32 unique discovery IDs, 52 unique cached IDs, and 16 exact set-difference metadata rows.
- Generated model IDs must equal four supported missing definitions and be disjoint from cached IDs.
- The runtime set must equal its 37-selector baseline plus the four additions, with no cached-selector deletion.
- Confirm cache/auth and non-NVIDIA config preservation, artifact hashes, source qualification, and no credentials.
- Unknown/unsupported candidates stay in evidence; they do not receive fabricated chat definitions or prices.
