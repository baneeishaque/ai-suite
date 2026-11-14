<!-- title: OpenCode rate-limit handling investigation on 2026-11-15 -->

# OpenCode Rate-Limit Handling Investigation

**Investigation date:** 2026-11-15 (local). **Incident window:** 2026-11-14 17:52–18:03 UTC.
**Software baseline:** OpenCode `1.19.5` on macOS. **Provider:** Experiential Labs (`explabs`).
**Model:** `gpt-6-luna:free`. **Status:** diagnosis documented; configuration changes remain recommendations.

## Executive Conclusion

The error is not an OpenCode defect. It is Experiential Labs enforcing the free-core token allowance on
`gpt-6-luna:free`. Two independent limits apply:

1. **Per-minute:** 250,000 tokens/minute for the core model. OpenCode retries this successfully by waiting for the
   provider's `Retry-After` window and trying again.
2. **Per-day:** 1,000,000 input plus output tokens per UTC day, shared across the free-core pool. This resets at
   00:00 UTC. OpenCode cannot usefully wait hours for that reset, so the turn stops.

OpenCode has **no per-provider or per-model retry, rate-limit, or fallback setting**. The configuration schema exposes
only provider timeouts, `baseURL`, credentials, and package-specific options. The only rate-limit-relevant lever inside
OpenCode is pointing a provider's `baseURL` at a gateway.

OmniRoute is the external gateway that provides the missing behavior: request queueing, connection cooldown, model
lockout, provider circuit breaking, and combo/fallback chains. It can smooth and fail over rate-limited traffic, but it
cannot create quota that Experiential Labs does not provide.

"Keep going on credits" is an **Experiential Labs account setting**, not an OpenCode setting.

## Reading Order

| Document | Question it answers |
| --- | --- |
| [README.md](README.md) | Full incident, mechanism, configuration audit, gateway options, and recommendations. |
| [sources.md](sources.md) | Primary public citations, verification scope, and qualifiers. |
| [AGENTS.md](AGENTS.md) | The owning contract for this investigation folder. |

## Original Questions and Their Disposition

| Question | Verified answer | Detailed owner |
| --- | --- | --- |
| What is `class_rate_limit`? | The provider's error class for a free-core token allowance rejection, wrapped by OpenCode as `AI_APICallError`. | [Exact observed errors](#exact-observed-errors) |
| Can OpenCode handle the rate limit? | It retries the per-minute limit by honoring `Retry-After`. It cannot wait out the daily limit. | [OpenCode retry mechanics](#opencode-retry-mechanics-v1195) |
| Is there a provider/model-specific retry setting? | No. The schema has no `retry`, `rateLimit`, or `fallback` key. | [Configuration audit](#configuration-audit) |
| What per-provider settings do exist? | `apiKey`, `baseURL`, `enterpriseUrl`, `setCacheKey`, `timeout`, `headerTimeout`, `chunkTimeout`. | [What does exist](#what-does-exist-and-is-not-a-rate-limit-knob) |
| Does OmniRoute have this feature? | Yes: rate-limit queue, cooldowns, lockouts, circuit breakers, and combo fallback. | [Gateway and failover options](#gateway-and-failover-options-omniroute) |
| What did maintainers say? | OpenCode maintainers closed v1 retry requests as v2-focused; OmniRoute's owner confirms it proxies upstream 429s and fails over only when a combo is configured. | [Maintainer and community responses](#maintainer-and-community-responses) |
| What should be changed? | Prefer the plain `gpt-6-luna` ID, reduce token burn, enable credits if paid continuation is acceptable, or front the provider with OmniRoute. | [Remediation and validation](#remediation-and-validation) |

## Incident Report

### Environment

- OpenCode `1.19.5` (macOS, arm64 binary).
- Provider `explabs`, configured as `@ai-sdk/openai-compatible` with
  `options.baseURL = https://api.experientiallabs.ai/v1`.
- Session model `gpt-6-luna:free`, agent `build`, primary mode.
- The incident was a long agent session with many tool steps; each step re-sends the conversation context.

### Exact observed errors

Per-minute rejection:

```text
AI_APICallError: class_rate_limit: This core model has a Free allowance of 250000 tokens/minute.
Enable Keep going on credits to continue, or wait for the reset.
```

Per-day rejection:

```text
AI_APICallError: org_token_rate_limit_day: Free core models share 1000000 input + output tokens per UTC day.
Enable Keep going on credits to continue, or wait for the reset. Retry after 00:00 UTC. Input and output tokens,
including cached input, count toward this shared core pool. Paid plans and BYOK are unaffected. Your organization's
limits and tier: https://platform.experientiallabs.ai/settings/limits
```

`class_rate_limit` and `org_token_rate_limit_day` are provider error classes. OpenCode surfaces them inside an
`AI_APICallError`. Both are 429-class responses.

### Chronology

All timestamps are UTC on 2026-11-14.

| Time | Observation |
| --- | --- |
| 17:52:53 | `class_rate_limit` (250,000 tokens/minute) |
| 17:53:53 | Next model attempt starts, about 60 seconds later; the retry succeeds |
| 17:55:59 | `class_rate_limit` again |
| 17:56:59 | Retry about 60 seconds later; succeeds |
| 17:57:21 | `class_rate_limit` again |
| 17:58:21 | Retry about 60 seconds later |
| 17:58:35 | `org_token_rate_limit_day` (1,000,000 tokens/day; retry after 00:00 UTC) |
| 18:03:32 | Session cancel |

### What OpenCode did

The approximately 60-second gaps after each per-minute rejection match the provider's `Retry-After` window. OpenCode
honored the header, waited, and retried the same turn. Those retries succeeded because the per-minute window reset.

After the daily rejection, the required wait was hours. The user cancelled the session. OpenCode did not invent a
shorter wait, and no configuration setting would have made the daily allowance larger.

### Evidence scope

- Incident-specific findings use the OpenCode runtime log and the incident session record.
- The exact session identifier and machine-local paths are intentionally excluded from this durable document.
- Provider behavior is taken from the public Experiential Labs pricing page and machine-readable contract.
- OpenCode behavior is taken from the installed `1.19.5` source and the public configuration schema.

## Root-Cause Analysis

### Two independent limits

Experiential Labs documents the free-core pool as shared across GPT-6 Luna, DeepSeek V4.1 Flash, and Clef:

| Limit | Free-core allowance | Reset |
| --- | ---: | --- |
| Requests | 10 requests/minute | Rolling minute |
| Tokens per minute | 250,000 tokens/minute per model | Rolling minute |
| Tokens per day | 1,000,000 input + output tokens shared | 00:00 UTC |

Cached input tokens count toward the shared daily pool. Paid plans and BYOK traffic are unaffected.

A `:free` model identifier is a free-only lane: past the allowance it stops and is never charged. The plain model
identifier is the core model that can continue on credits after the free allowance.

### OpenCode retry mechanics (v1.19.5)

The installed version uses `packages/opencode/src/session/retry.ts`:

| Constant | Value |
| --- | ---: |
| `RETRY_INITIAL_DELAY` | 2000 ms |
| `RETRY_BACKOFF_FACTOR` | 2 |
| `RETRY_JITTER_FACTOR` | 0.25 |
| `RETRY_MAX_DELAY_NO_HEADERS` | 30,000 ms |
| `RETRY_MAX_DELAY` | 2,147,483,647 ms |
| `RETRY_MAX_RETRIES` | 5 |

Behavior:

- 429, `rate_limit`, `too many requests`, and similar messages are classified as retryable.
- `retry-after` and `retry-after-ms` response headers take priority over local backoff.
- Without those headers, backoff is 2 s, 4 s, 8 s, 16 s, then capped at 30 s.
- After five attempts the policy gives up.
- A provider `Retry-After` is not capped in v1, so a multi-hour header can produce a multi-hour silent wait.

### OpenCode v2 differences

OpenCode 2.0 replaced the retry policy in `packages/core/src/model-retry.ts`:

- 10 retries, exponential from 2 s capped at 10 s per gap, about 84 seconds of waiting per exhausted cycle.
- A provider-requested wait is capped at 15 minutes (`RETRY_AFTER_MAX`).
- A `session.retry` plugin hook can change the retry decision or delay, but the built-in attempt cap remains a hard
  limit.
- No configurable `maxRetries` key exists; the request is tracked in issue #54862.
- No model fallback chain exists; the request is tracked in issue #48991.
- Pause-until-reset and auto-resume are tracked in issue #43126.
- Time-based model availability with cross-provider fallback is proposed in PR #63728.

### Why the per-minute limit recovered

The provider's `Retry-After` was about 60 seconds. OpenCode waited that long and retried. The rolling minute window
reset, so the next attempt succeeded. This is the intended behavior and required no configuration change.

### Why the daily limit did not

The daily allowance resets at 00:00 UTC. No retry policy can make the provider ignore a daily cap. Waiting is the only
client-side option, and the wait is hours. OpenCode v1 would honor a multi-hour `Retry-After` (with a silent wait); v2
caps the wait at 15 minutes and then fails.

### Limits of this analysis

- The exact `Retry-After` header values were not captured in the durable record; the 60-second spacing is consistent
  with the provider's documented per-minute window.
- The provider's live allowance, plan state, and account tier can change.
- The analysis does not claim that every provider behaves like Experiential Labs.

## Configuration Audit

### OpenCode config schema (verified)

The public schema at `opencode.ai/config.json` was checked on 2026-11-14. There is no `retry`, `rateLimit`,
`maxRetries`, `fallback`, or `rpm`/`tpm` key at the root, provider, or model level.

### What does not exist

- No per-provider or per-model retry count, backoff, or jitter setting.
- No per-provider or per-model rate-limit threshold or token budget.
- No automatic model fallback chain.
- No pause-until-reset or auto-resume setting.
- No circuit breaker or shared cross-session backoff.

### What does exist (and is not a rate-limit knob)

Provider-level keys:

```text
api, name, env, id, npm, whitelist, blacklist, options, models
```

Provider `options` keys:

```text
apiKey, baseURL, enterpriseUrl, setCacheKey, timeout, headerTimeout, chunkTimeout
```

Model-level keys include `settings`, `headers`, `body`, `capabilities`, `limit`, `variants`, `cost`, and `disabled`.
`settings` is provider-package-specific and does not control retries.

### Closest levers

- `provider.exlabs.options.baseURL`: point OpenCode at a gateway such as OmniRoute.
- `model`: select a different model.
- `small_model`: use a cheaper model for title generation.
- `compaction.auto` and `compaction.keep.tokens`: reduce context size and token burn.
- `disabled_providers` / `enabled_providers`: hide or expose providers.
- `provider.exlabs.options.timeout`, `headerTimeout`, `chunkTimeout`: transport timeouts only, not rate limits.

## Gateway and Failover Options (OmniRoute)

### What OmniRoute provides

OmniRoute is a local OpenAI-compatible gateway, default `http://localhost:20128/v1`. Its rate-limit machinery includes:

- Request queue and admission pacing with upstream `Retry-After` detection.
- Connection cooldown on 429, model lockout, and a provider circuit breaker.
- Combo/fallback chains with `fill-first` or `priority` strategy.
- Wait-for-cooldown: if every candidate is cooling down, it can wait for the earliest and retry the same request.
- Per-provider exponential backoff settings.

### Exact settings

From the OmniRoute environment contract:

| Variable | Default | Purpose |
| --- | ---: | --- |
| `RATE_LIMIT_MAX_WAIT_MS` | 30000 | Maximum queue wait before a request fails |
| `RATE_LIMIT_EXECUTION_MAX_WAIT_MS` | 600000 | Maximum admitted execution time |
| `RATE_LIMIT_MAX_QUEUE_DEPTH` | 0 | Queue admission cap; 0 is unbounded |
| `RATE_LIMIT_AUTO_ENABLE` | unset | Force the auto-enable safety net on or off |
| `PROVIDER_COOLDOWN_MIN_MS` | 5000 | Minimum failed-provider cooldown |
| `PROVIDER_COOLDOWN_MAX_MS` | 300000 | Maximum failed-provider cooldown |
| `OMNIROUTE_ROTATE_ON_400` | false | Rotate on 400/401 responses |
| `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT` | 1 | Heavy-request admission ceiling |
| `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS` | tracks `RATE_LIMIT_MAX_WAIT_MS` | Heavy-request queue wait |

### Maintainer statements

- OmniRoute proxies upstream 429 responses; it does not manufacture quota.
- On a 429, connection cooldown skips that connection, and a configured combo fails over to the next target.
- Free-tier OpenCode quotas are IP-based; distinct rotation requires a distinct egress IP per connection.
- Auto rate-limit protection applies to API-key providers, not OAuth or subscription providers.

### Integration

OmniRoute ships an OpenCode setup command that writes an OpenAI-compatible provider entry. The manual equivalent is a
provider with `npm: @ai-sdk/openai-compatible`, `options.baseURL: http://localhost:20128/v1`, and an API key from the
OmniRoute dashboard. Point an existing provider's `baseURL` at the gateway to front it.

### What OmniRoute cannot do

OmniRoute cannot raise Experiential Labs' 1,000,000 tokens/day free-core cap. It can queue requests, cooldown the
limited connection, and fail over to a different model or provider in a combo. If every target shares the same upstream
account or egress IP, the provider-side cap still applies.

## Remediation and Validation

### Recommended actions (prioritized)

1. **Use the plain `gpt-6-luna` identifier for long agent sessions.** The `:free` lane is free-only and stops at the
   allowance. The plain identifier is a core model that can continue on credits.
2. **Reduce token burn.** Set `small_model`, keep automatic compaction on, lower `compaction.keep.tokens`, and avoid
   unnecessary parallel subagents.
3. **Enable "Keep going on credits"** at `platform.experientiallabs.ai/credits` if paid continuation is acceptable.
   This is an account-level Experiential Labs setting.
4. **Front the provider with OmniRoute** if automatic queueing, cooldown, and failover are required. Configure a combo
   with a fallback target that does not share the same quota.
5. **Upgrade to OpenCode v2 and use a `session.retry` plugin** only to tune delays. The built-in attempt cap remains.
6. **Schedule long work away from the 00:00 UTC reset** when the daily cap is the binding constraint.

### Validation criteria

- A long agent session on the chosen model completes without `class_rate_limit` or `org_token_rate_limit_day`.
- `opencode models` lists the intended model and a test prompt returns a complete reply.
- If OmniRoute is used, its dashboard shows queue, cooldown, or failover events for the rate-limited target.
- Provider usage and cost are read after the test; a free-only expectation requires a zero cost meter.

### Non-recommendations

- Do not raise the OpenCode retry count expecting it to solve a daily cap.
- Do not treat `timeout`, `headerTimeout`, or `chunkTimeout` as rate-limit controls.
- Do not assume a gateway creates additional provider quota.

## Maintainer and Community Responses

| Project | Respondent | Summary |
| --- | --- | --- |
| OpenCode | `thdxr` (member) | v1 issues closed; development is v2-focused. |
| OpenCode | `neriousy` (member) | Zen free-tier and Go usage-limit errors are classified as quota exhaustion since v2.0.6. |
| OpenCode | `opencodejr` (bot) | The `session.retry` hook exists; the attempt cap is hard; fallback and pause-until-reset are unimplemented. |
| OmniRoute | `diegosouzapw` (owner) | Upstream 429s are proxied; combos fail over; free-tier rotation needs distinct egress IPs. |

## Scope and Confidence

- Incident-specific findings use the OpenCode runtime log and the incident session record.
- Provider limits and error classes are source-derived from the public Experiential Labs contract.
- OpenCode retry behavior is source-derived from the installed v1.19.5 source and the public schema.
- OmniRoute behavior is source-derived from its public documentation and environment contract.
- No API keys, prompt bodies, browser cookies, or account-session material are included.
- The investigation does not assert that all providers or all OpenCode versions behave identically.

## Navigation

- [OpenCode documentation home](../../README.md)
- [Experiential Labs operations guide](../../providers/experiential-labs/README.md)
- [Experiential Labs research](../../../../research/opencode/providers/experiential-labs/README.md)
- [Source register](sources.md)
