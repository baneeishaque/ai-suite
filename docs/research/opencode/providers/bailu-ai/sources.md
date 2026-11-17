<!-- title: Bailu AI provider research primary sources and qualifications -->

# Sources and Evidence Qualifications

| Source | Scope |
| --- | --- |
| [Bailu home](https://bailucode.com/) | Product/model descriptions and links; marketing text is a claim, not serving proof. |
| [Open Platform](https://bailucode.com/openapi/) | Current API base and platform entry point. |
| [API platform](https://bailucode.com/api_platform/) | Logged-in account quota/key usage, catalog classes, and documentation. |
| [Platform implementation](https://bailucode.com/api_platform/src/api_platform.js) | Actual `get_stats`, `get_keys`, catalog, quota units, and lazy-documentation retrieval contracts. |
| [Documentation fragment](https://bailucode.com/api_platform/components/documentation) | Chat Completions/Messages/Responses/media request shapes; does not itself establish current serving availability. |
| [Bailu CLI](https://github.com/CheYu0410/Bailu-Cli) | Provider-linked client/reference; source features are not proof that every gateway model works. |
| [OpenCode v1 provider schema](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/core/src/v1/config/provider.ts) | Version-tagged legacy fields and blacklist/options structure; installed runtime verification remains authoritative. |
| [OpenCode published schema](https://opencode.ai/config.json) | Moving schema; legacy and modern field presence does not prove installed support. |

API/catalog/account sources were checked during the 2026-11-17 audit. They are dated observations.
Direct curl and OpenCode records are separate datasets; neither is substituted for the other.
Account/key identity is established by matching fingerprints without publishing any key or credential fragment.
The [manifest](evidence/manifest.json) binds relative portable evidence files to SHA-256 and observation/count scope.
