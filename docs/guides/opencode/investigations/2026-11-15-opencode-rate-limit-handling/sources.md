<!-- title: Source register for the OpenCode rate-limit handling investigation -->

# Source Register

Each entry states what was checked, on what date, and how far the evidence supports the investigation's claims.

## Provider Sources

| Source | URL | Verification scope |
| --- | --- | --- |
| Experiential Labs pricing | [experientiallabs.ai/pricing](https://www.experientiallabs.ai/pricing) | Free-core models, 10 RPM, 250K TPM, 1M tokens/day, 00:00 UTC reset, plan table. Checked 2026-11-14. |
| Experiential Labs machine-readable contract | [platform-experientiallabs ai/llms.txt](https://platform.experientiallabs.ai/llms.txt) | Free-core continuation, `:free` semantics, error classes `rate_limit_exceeded`, `free_limit_reached`, `insufficient_quota`, `Retry-After` guidance. Checked 2026-11-14. |
| Experiential Labs account limits page | [platform-experientiallabs ai/settings/limits](https://platform.experientiallabs.ai/settings/limits) | Referenced by the provider's daily-limit error message; account-scoped and requires sign-in. Not scraped. |
| Experiential Labs agents page | [experientiallabs.ai/agents](https://www.experientiallabs.ai/agents) | Gateway description, OpenAI-compatible endpoint, provider failover claim. Checked 2026-11-14. |

## OpenCode Sources

| Source | URL | Verification scope |
| --- | --- | --- |
| OpenCode configuration reference | [opencode.ai/docs/config](https://opencode.ai/docs/config) | Configuration locations, provider/model options, schema pointer. Checked 2026-11-14. |
| OpenCode providers reference | [opencode.ai/v2/docs/providers](https://opencode.ai/v2/docs/providers/) | Provider fields, `settings`, `headers`, `body`, timeout fields, retry behavior for timeouts. Checked 2026-11-14. |
| OpenCode models reference | [opencode.ai/docs/models](https://opencode.ai/docs/models) | Model selection, `settings`/`headers`/`body`, variants, limits. Checked 2026-11-14. |
| OpenCode plugin server hooks | [opencode.ai/v2/docs/build/plugins/server](https://opencode.ai/v2/docs/build/plugins/server) | `session.retry` hook contract and the hard attempt cap. Checked 2026-11-14. |
| OpenCode configuration schema | [opencode.ai/config.json](https://opencode.ai/config.json) | Machine-readable schema used to confirm the absence of retry/rate-limit/fallback keys. Checked 2026-11-14. |
| OpenCode v1 retry source | [session/retry.ts at v1.19.5](https://github.com/anomalyco/opencode/blob/v1.19.5/packages/opencode/src/session/retry.ts) | Retry constants, retryable patterns, `retry-after` handling, five-attempt cap. |
| OpenCode v2 model retry source | [core/model-retry.ts](https://github.com/anomalyco/opencode/blob/dev/packages/core/src/model-retry.ts) | Ten-attempt schedule, 15-minute `RETRY_AFTER_MAX`, unreachable and timeout budgets. |
| OpenCode session runner retry | [session/runner/retry.ts at v2.2.0](https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/session/runner/retry.ts) | v2 retry decision flow and `session.retry` hook invocation. |

## OpenCode Issue and Pull Request Sources

| Source | URL | Verification scope |
| --- | --- | --- |
| Issue #30510 | [Rate limit retries with no backoff](https://github.com/anomalyco/opencode/issues/30510) | Rate-limit retry loop report; documents the retry policy's history. |
| PR #41939 | [Cap session retries with jitter](https://github.com/anomalyco/opencode/pull/41939) | Introduced the five-attempt cap and jitter in v1. |
| Issue #43596 | [Configurable retry policy](https://github.com/anomalyco/opencode/issues/43596) | Request for configurable retry policy; closed as v2-focused. |
| Issue #54862 | [Retry hook after the built-in cap](https://github.com/anomalyco/opencode/issues/54862) | Request to let the `session.retry` hook run after the built-in cap; open. |
| Issue #48991 | [Configurable model fallback](https://github.com/anomalyco/opencode/issues/48991) | Request for configurable model fallback; open. |
| Issue #43126 | [Pause and resume on reset](https://github.com/anomalyco/opencode/issues/43126) | Request for pause-until-reset and auto-resume; open. |
| Issue #57049 | [Silent wait on a large retry-after](https://github.com/anomalyco/opencode/issues/57049) | v1 silent multi-hour wait on a large `Retry-After`; v2 caps at 15 minutes. |
| Issue #43324 | [Per-provider quota-aware retry](https://github.com/anomalyco/opencode/issues/43324) | Per-provider quota-aware retry and reset schedule proposal. |
| Issue #55075 | [No shared provider backoff](https://github.com/anomalyco/opencode/issues/55075) | No shared per-provider backoff or circuit breaker across sessions. |
| PR #63728 | [Time-based model availability](https://github.com/anomalyco/opencode/pull/63728) | Time-based model availability with cross-provider fallback; in review. |

## OmniRoute Sources

| Source | URL | Verification scope |
| --- | --- | --- |
| OmniRoute troubleshooting guide | [TROUBLESHOOTING.md](https://github.com/diegosouzapw/OmniRoute/blob/main/docs/guides/TROUBLESHOOTING.md) | Free-provider rate-limit symptoms, rotation, concurrency, and fallback tuning. Checked 2026-11-14. |
| OmniRoute environment contract | [.env.example](https://github.com/diegosouzapw/OmniRoute/blob/main/.env.example) | `RATE_LIMIT_*`, `PROVIDER_COOLDOWN_*`, and chat admission variables with defaults. Checked 2026-11-14. |
| OmniRoute user guide | [USER_GUIDE.md](https://github.com/diegosouzapw/OmniRoute/blob/main/docs/guides/USER_GUIDE.md) | Resilience components, fallback chains, wait-for-cooldown, rate-limit auto-detection. Checked 2026-11-14. |
| OmniRoute OpenCode framework guide | [OPENCODE.md](https://github.com/diegosouzapw/OmniRoute/blob/main/docs/frameworks/OPENCODE.md) | OpenCode integration path and generated provider configuration. Checked 2026-11-14. |
| OmniRoute issue #9611 | [Free-tier 429 rotation](https://github.com/diegosouzapw/OmniRoute/issues/9611) | Owner statement that upstream 429s are proxied and free-tier quotas are IP-based. |
| OmniRoute discussion #10678 | [OpenCode Zen rate limits](https://github.com/diegosouzapw/OmniRoute/discussions/10678) | Owner statement on connection cooldown and combo failover for free-tier limits. |

## Qualifiers

- Provider pages and quotas are moving targets. The dated values in the investigation are evidence, not a promise.
- OpenCode v1 and v2 retry behavior differ; the investigation labels which version each claim describes.
- OmniRoute settings are documented defaults; a deployment can override them in the dashboard or environment.
- No source in this register is used to assert account-specific quota, cost, or plan state.
