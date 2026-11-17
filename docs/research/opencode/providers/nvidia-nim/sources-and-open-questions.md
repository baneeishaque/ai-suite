<!-- title: NVIDIA NIM primary sources and unresolved inference questions -->

# Sources and Open Questions

## Primary Sources

- [NVIDIA NIM catalog](https://build.nvidia.com/models) — downloadable/public model entries,
  including non-chat/preview use.
- [Authenticated model discovery](https://integrate.api.nvidia.com/v1/models) — exact API IDs; requires a NVIDIA API key.
- [Mistral Large 4 hosted reference](https://build.nvidia.com/mistralai/mistral-large-4-1t-a52b/apireference.md).
- [Ising Calibration hosted reference](https://build.nvidia.com/nvidia/ising-calibration-1.5-31b/apireference.md).
- [Nemotron Bolt hosted reference](https://build.nvidia.com/nvidia/nemotron-3.5-bolt-e4b/apireference.md).
- [Riva Translate hosted reference](https://build.nvidia.com/nvidia/riva-translate-4b-instruct-v2/apireference.md).
- [Riva Translate model card](https://build.nvidia.com/nvidia/riva-translate-4b-instruct-v2.md).
- [Topic-control reference](https://build.nvidia.com/nvidia/llama-3_1-nemoguard-8b-topic-control/apireference.md).
- [Kimi K3.1 Pro preview card](https://build.nvidia.com/moonshotai/kimi-k3_1-pro.md) — explicitly no programmatic API access.
- [OpenCode configuration schema](https://opencode.ai/config.json) — fields must also match installed OpenCode behavior.

The authenticated catalog was captured on 2026-11-17; source-specific observation times/statuses are in the metadata.
API `created` timestamps are retained as supplied, not interpreted as verified public release dates.
Conflicting vendor versus hosted limits are not silently merged.

## Remaining Questions

- **Serving/tool compatibility:** no inference was performed. Resolve with separately scoped, funding-qualified
  real assistant/SSE/tool-result probes rather than treating model-list presence as working-model proof.
- **Preview access:** public pages can precede key access; add a newly released ID only after actual API discovery
  and its supported hosted contract match.
- **Specialized endpoints:** embeddings, rerankers, topic classifiers, and video/audio services require their own
  client contracts. Do not advertise them as assistant chat merely to increase model count.
- **Riva context shorthand:** 8K is mapped to 8,192 tokens as documented in this research; a precise published hosted
  numeric context bound should replace that interpretation when available.
- **Stale cached metadata:** the task intentionally preserves existing cache entries. This supplement does not
  repair their limits, modalities, prices, retirement status, or availability.
