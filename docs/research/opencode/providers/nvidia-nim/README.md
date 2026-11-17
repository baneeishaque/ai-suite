<!-- title: NVIDIA NIM APIs and cache-aware OpenCode model supplements -->

# NVIDIA NIM APIs and OpenCode Integration

NVIDIA NIM provides hosted API endpoints as well as downloadable/deployable inference microservices.
This research records the 2026-11-17 catalog/configuration reconciliation using OpenCode **1.19.5**.
It fills current cache gaps through `provider.nvidia.models` without replacing cached metadata.

## Result

| Layer | Count |
| --- | ---: |
| Current OpenCode cache's NVIDIA definitions | 52 |
| Original effective `opencode models nvidia` selectors | 37 |
| Authenticated `GET /v1/models` IDs | 32 |
| API IDs absent from the cache | 16 |
| Added documented assistant/translation chat definitions | 4 |
| Final effective runtime selectors | 41 |

The supplement has **zero exact-ID overlap** with the cache. All original runtime selectors remain present.
Discovery includes embeddings and specialized services; those missing IDs are documented without being represented
as chat models. Public playground pages also include models without programmatic API access.

## Added Models

| Exact NVIDIA API ID | Display name | Context / output ceiling | Documented features |
| --- | --- | --- | --- |
| `mistralai/mistral-large-4-1t-a52b` | Mistral Large 4 | 262144 / 262144 | Text/image, tools, reasoning |
| `nvidia/ising-calibration-1.5-31b` | ising-calibration-1.5-31b | 262144 / 32768 | Text/image quantum calibration; no tools/reasoning |
| `nvidia/nemotron-3.5-bolt-e4b` | Nemotron 3.5 Bolt E4B | 65536 / 65536 | Text, tools, reasoning |
| `nvidia/riva-translate-4b-instruct-v2` | riva-translate-4b-instruct-v2 | 8192 / 4096 | Text translation; language-code system prompt |

For a model whose API ID begins `nvidia/`, the OpenCode selector contains the provider prefix too:
`nvidia/nvidia/nemotron-3.5-bolt-e4b`. This is intentional, not a duplicated API ID.

## Verification Scope

Verified: authenticated catalog retrieval, first-party endpoint schemas, metadata/limit extraction, zero overlap,
fresh candidate/saved OpenCode model-list union, cache/auth bytes, and non-NVIDIA configuration preservation.

No inference/generation request was made. Listed capabilities are documented endpoint features, not exhaustive live
quality/availability/tool-round-trip results. No free-access suffix or zero price was fabricated from a missing estimate.

## Reading Order

1. [Cache and supplement](cache-and-supplement.md)
2. [API contracts and limits](api-contracts-and-limits.md)
3. [Refresh and verify](refresh-and-verify.md)
4. [Sources and open questions](sources-and-open-questions.md)
5. [Portable evidence](evidence/README.md)
