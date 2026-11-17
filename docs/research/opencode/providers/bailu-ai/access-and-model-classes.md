<!-- title: Bailu access, native classes, and observed failure meanings -->

# Access and Model Classes

## Current Account Scope

The authenticated platform reported `user_api_level: 1`. A key can advertise a model that is unavailable upstream.
Platform-only higher-level entries remain access-gated; the audit does not pay, upgrade, or fabricate entitlement.

## Native and Unsupported Classes

Image/video/music generation, embeddings, and the documented native OCR route are excluded from the ordinary
OpenCode text/tool picker. No native generation job was submitted for this classification.
Native entries remain in the configuration/evidence with explicit blacklist reasons.

## Observed Response Categories

| Evidence | Interpretation |
| --- | --- |
| HTTP 400 `model_not_found` for an old ID | The current gateway rejects that exact model ID. |
| HTTP 404 with “temporarily unavailable” | Advertisement is not serving proof; qualify the actual message rather than declare permanent retirement. |
| HTTP 429 `upstream_busy` | Provider/upstream availability limitation, distinct from account monetary balance. |
| HTTP 502 / edge error body | Current upstream/transport failure; not a complete model reply. |
| HTTP 200 empty/wrong/truncated content | Not a passed chat completion. |
| Text passes but required function/result test fails | The intended coding-client profile is not verified; exclude it. |
| OpenCode fixture permission error | Harness permission issue; correct the exact scoped permission and retest before a model verdict. |
| Provider/account credit or payment requirement | Blacklist and retain the actual error; do not fund either account or upstream wallet. |

The initial read-tool harness used an absolute-only read rule. OpenCode evaluates the relevant relative path,
so the final harness explicitly allows only the same nonce file's absolute/actual relative paths and its external
directory scope. The corrected client test then passed; the harness error was not mislabelled provider failure.

See the [direct results](evidence/direct-api-probe-results.csv), [client results](evidence/opencode-probe-results.csv),
and [per-model policy](evidence/model-policy.csv) for complete source-qualified dispositions.
