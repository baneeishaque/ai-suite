<!-- title: NVIDIA model cache authority and minimal supplemental definitions -->

# Cache Authority and Supplemental Definitions

## Source Layers

- **OpenCode cache:** models.dev-derived NVIDIA definitions. It remains unchanged by this workflow.
- **Authenticated discovery:** exact key-advertised API IDs from `https://integrate.api.nvidia.com/v1/models`.
- **NVIDIA model catalog/cards:** public descriptions and metadata, including preview/playground entries.
- **Hosted API reference:** method, URL, schema, model-ID enum/default, tools/modalities, and parameter ceilings.
- **Configuration supplement:** only qualified exact IDs absent from the cache.
- **Runtime catalog:** the actual provider/model selectors from a fresh installed OpenCode process.

These are different counting units. This snapshot contains 52 cached definitions but only 37 baseline runtime
selectors. The reconciliation preserves that baseline rather than forcing all cached entries visible or replacing
cached metadata. It adds four definitions and proves the final set is the original 37 plus those four.

## Invariant

```text
C = exact IDs in the current cache.nvidia.models
A = authenticated current API IDs
Q = missing API IDs with a documented supported chat contract and usable limits
S = Q minus C
generated supplement IDs intersect C = empty set
effective runtime after = effective runtime before union S
```

User-defined provider settings and existing custom definitions are separately preserved and reported.
The workflow does not manufacture models from a page title, URL slug, marketing counter, or vendor checkpoint name.
NVIDIA page slugs may use underscores while the real API ID uses dots; an apparent page 404 alone is not retirement.

## Gradual Cache Convergence

Whenever the cache is updated through the user's ordinary workflow, rerun collection/metadata/sync against the new cache.
Use the persistent `nvidia-nim-supplement-ownership.json` sidecar next to the global config to identify definitions
that the generator owns:

1. If an unchanged managed model is now cached, remove only its supplemental definition.
2. If a managed model temporarily disappears from authenticated discovery but remains uncached, preserve it and report
   `managed_not_advertised_ids`; catalog disappearance alone is not deletion authority.
3. If a managed definition has been edited, stop for review instead of deleting user content.
4. Preserve unrelated provider options, user overrides, credentials, and cache bytes.

This lets the cache take over IDs naturally without accumulating duplicate configuration copies.
Refreshing models.dev alone is not assumed to fill NVIDIA's current gaps.
