<!-- title: Bailu AI OpenCode provider research -->

# Bailu AI OpenCode Provider Research

This research explains the 2026-11-17 Bailu model audit and the verified-free OpenCode picker policy.
The runtime provider is `bailucode`, using `https://bailucode.com/openapi/v1` through the OpenAI-compatible SDK.

## Snapshot

- 46 definitions existed before the audit.
- Authenticated OpenAI discovery advertised 28 IDs; the logged-in platform published 38 IDs across model classes.
- Their exact-ID union with the retained definitions contained 60 models.
- Nine models passed direct text, SSE, function invocation/result, and real OpenCode text/read-tool checks.
- The final configuration retains 60 definitions and blacklists 52; eight admitted display names have one `(free)`.
- `bailu-edge` passed isolated checks but failed final saved routing with upstream unavailability; it is blacklisted.
- The matched account/key reports nonmonetary token allowance and zero recorded price. Free tokens are still consumed.
- Recorded request usage did not explain the aggregate matched-key token increase; research qualifies that gap and
  no further inference was run after it was identified.
- Final saved-routing verification and evidence publication are recorded in the datasets/history, not inferred from counts.

## Reading Order

1. [Catalog layers](catalog-layers.md) — what each count and identity means.
2. [Access and model classes](access-and-model-classes.md) — disabled, native, retired, blocked, and incomplete cases.
3. [Free model and billing policy](free-model-and-billing-policy.md) — why free is independent of a cost estimate.
4. [Input length and workspace context](input-data-length-and-workspace-context.md) — controlled client diagnostics.
5. [Implementation history](implementation-history.md) — actual configuration and verification progression.
6. [Sources](sources.md) and [evidence](evidence/README.md) — portable supporting records.
7. [Open questions](open-questions.md) — remaining limits of the evidence.

## Final Verified Client List

| Exact ID | API-provided display name with free annotation |
| --- | --- |
| `bailu-2.8-nvfp8` | BaiLu 2.8 NVFP8 (free) |
| `bailu-2.9-preview` | BaiLu 2.9 Preview 20261101 (free) |
| `bailu-apex-2.1` | BaiLu Apex 2.1 (free) |
| `bailu-apex-2.5` | BaiLu Apex 2.5 (free) |
| `bailu-apex-2.6` | BaiLu Apex 2.6 (free) |
| `bailu-apex-2.7` | BaiLu Apex 2.7 (free) |
| `bailu-apex-openclaw` | BaiLu Apex OpenClaw (free) |
| `yuyu-air` | Yuyu Air (free) |

These are dated observed results, not availability guarantees. The evidence table distinguishes direct, isolated,
and saved-route outcomes. The visible profiles advertise only verified text/tool capability; optional media input
is not claimed from provider metadata alone.
