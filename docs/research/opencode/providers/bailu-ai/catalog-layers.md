<!-- title: Bailu model catalog layers and exact-ID accounting -->

# Catalog Layers and Exact-ID Accounting

## Different Sets

| Layer | 2026-11-17 count | Meaning |
| --- | ---: | --- |
| Pre-audit configuration | 46 | Existing local definitions, including stale/native models. |
| Key-advertised discovery | 28 | `GET /openapi/v1/models` with the persisted key. Advertisement is not serving proof. |
| Platform catalog | 38 | Model and native-class arrays from authenticated `/api/getmodels`. |
| Audit universe | 60 | Exact-ID union of retained configuration, key discovery, and platform rows. |
| Approved candidate definitions | 60 | Retained for complete model accounting. |
| Final blacklist | 52 | Excluded from the ordinary OpenCode chat picker. |
| Final visible set | 8 | Verified-free direct, isolated, and saved-routing clients. |

Platform arrays include `models`, `image_models`, `video_models`, `music_models`, `ocr_models`, and
`embedding_models`. Its `model_type` values such as `hot`, `web`, `internal`, and empty strings are presentation
categories, not reliable chat/native type declarations. Collection membership establishes the native class.

## Identity Rules

- Preserve IDs exactly, including `Yuyu`, `2B`, and `30B` capitalization. Do not normalize identities by display name.
- An API name is optional. Use its provided string, otherwise the exact ID; append the free annotation separately.
- Historical `bailu-apex-2.1-lite` differs from current `bailu-apex-2.1`; `bailu-edge-8b` differs from `bailu-edge`.
- Newly advertised `bailu-2.8-fast` is a distinct ID, not an inferred alias.
- Native models can use a Chat Completions-shaped endpoint without providing the text/tool semantics OpenCode needs.
- Retained unavailable definitions belong to the audit/blacklist sets, not the current serving set.

The [model inventory](evidence/model-inventory.csv) contains one row per exact ID and every source-membership flag.
The [reconciliation summary](evidence/catalog-reconciliation-summary.json) proves the set/count relationships.
