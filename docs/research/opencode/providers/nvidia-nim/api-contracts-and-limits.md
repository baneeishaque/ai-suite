<!-- title: NVIDIA NIM hosted endpoint contracts and documented model limits -->

# API Contracts and Limits

## Hosted Chat API

The four added models declare `POST https://integrate.api.nvidia.com/v1/chat/completions` and a bearer NVIDIA API key.
Use their exact API model ID in the request; the OpenCode provider prefix is not part of the API ID.
Schemas include SSE streaming and assistant-text output. Some NIM endpoints document HTTP 202 pending responses
and NVCF request-ID polling; a pending submission is not a completed response.

Credential handling uses the persisted OpenCode `nvidia` auth entry. Catalog GET credentials are passed through
curl's stdin configuration rather than command arguments or URLs. Chrome metadata is read in a background tab
without exporting cookies, local-storage values, account identity, or browser control to the foreground.

## Model-Specific Details

- **Mistral Large 4:** the upstream/model description mentions a larger window, but the hosted API contract specifies
  a combined 262,144-token window. The hosted `max_tokens` schema ceiling is also 262,144; prompt/reasoning/output
  together must still fit. It supports up to eight image inputs, tools, reasoning, and SSE; audio/video are unsupported.
  The schema says `reasoning_effort` accepts the hosted options and omitted requests behave differently from the
  playground default. No guessed provider-wide reasoning control is added.
- **Nemotron 3.5 Bolt E4B:** the card specifies 65,536 context tokens; the hosted schema specifies a 65,536 output
  parameter ceiling. These ceilings are not a promise of simultaneous full-size input and output. Tools/reasoning
  and separate `reasoning_content` are documented. The full-precision model is primarily intended for customization
  and research rather than a blanket production-quality guarantee.
- **Ising Calibration 1.5:** a 262,144-token text/image VLM for quantum-calibration plots; maximum requested output
  is 32,768. Its card explicitly says tools/reasoning are unsupported. Large images may require NVCF asset handling.
- **Riva Translate v2:** a specialized text translation model. The published context shorthand is 8K, interpreted
  as 8,192 tokens; the hosted schema has a 4,096-token output ceiling. Examples use a language-pair system message
  such as `en-zh-cn`; it is not presented as a general coding/tool model.

## Missing IDs Not Added

All 16 cache-missing discovery IDs are recorded in [metadata evidence](evidence/missing-model-metadata.json).
Exclusions include embeddings, video detection, legacy/unresolved endpoint contracts, and topic-control classification.
The topic-control page uses an underscore route and returns classification text such as `off-topic`; it is not admitted
as an ordinary assistant model solely because its transport resembles Chat Completions.

The public **Kimi K3.1 Pro** page explicitly says no API key authorizes programmatic access yet; it is preview/playground
only and absent from the authenticated 32-ID discovery. It is therefore not added from a public card alone.

## Price and Availability Qualification

No monetary cost estimates, free annotation, live inference availability, latency, or billing consumption were
asserted from discovery alone. Trial/cloud-hosted and self-hosted licensing/access are distinct; consult the current
NVIDIA account and model-specific terms for actual inference use.
