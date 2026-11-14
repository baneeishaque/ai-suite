# Rate Limiting Handling Guide

**Date:** 2026-11-15  
**Author:** OpenCode Agent  
**Version:** 1.0

---

## 1. Overview

This document provides comprehensive guidance on handling rate limiting when using OpenCode with various AI model providers.
It addresses the `org_token_rate_limit_day` error encountered when using Experiential Labs AI's free core models,
and provides solutions for provider-specific rate limits (RPM, TPM, daily caps).

### 1.1 Scope

- **Audience:** OpenCode users experiencing rate limit errors
- **Purpose:** Explain rate limit types, OpenCode's capabilities, plugin solutions, and configuration patterns
- **Applicability:** All OpenCode users working with external AI model providers

### 1.2 Related Documentation

| Doc | Location | Purpose |
| ----- | ---------- | --------- |
| this guide | `docs/guides/opencode/investigations/2026-11-15-opencode-rate-limit-handling/rate-limiting-handling-guide.md` | Comprehensive rate limit handling |
| companion implementation plan | `docs/guides/opencode/investigations/2026-11-15-opencode-rate-limit-handling/rate-limiting-implementation-plan.md` | Step-by-step application of this guide |
| owning incident report | `docs/guides/opencode/investigations/2026-11-15-opencode-rate-limit-handling/README.md` | Verified incident analysis for this limit |
| OpenCode providers docs | `~/.config/opencode/opencode.jsonc` | Provider declaration and model configs |
| OpenCode auth management | `~/.config/opencode/auth.json` | API key storage |
| OmniRoute resilience guide | OmniRoute dashboard / `docs/reference/API_REFERENCE.md` | Advanced rate limit features (if using OmniRoute) |

---

## 2. Rate Limit Types Encountered

### 2.1 Organization Daily Token Cap (`org_token_rate_limit_day`)

**Error Message:**

```text
org_token_rate_limit_day: Free core models share 1000000 input + output tokens per UTC day.
Enable Keep going on credits to continue, or wait for the reset. Retry after 00:00 UTC.
```

**Characteristics:**

- **Scope:** Organization-wide daily limit
- **Reset:** UTC midnight (00:00 UTC)
- **Affected:** All free core models shared across the organization
- **Unaffected:** Paid plans, BYOK (Bring Your Own Key)
- **Source:** Provider's organizational quota management

**Impact:** All requests until the next UTC midnight reset, regardless of model or concurrency settings.

### 2.2 Per-Minute Requests Per Minute (RPM)

**Characteristics:**

- **Scope:** Per-minute request limit per model/provider
- **Typical free-tier values:** 20-40 RPM (NVIDIA NIM), varies by provider
- **Trigger:** Exceeded by concurrent or rapid sequential requests
- **Recovery:** Wait for minute window to reset, or use backoff/retry

### 2.3 Per-Day Token Limits (TPM)

**Characteristics:**

- **Scope:** Per-day total token consumption limit
- **Typical free-tier values:** Varies significantly by provider
- **Trigger:** Cumulative token usage across all requests in a UTC day
- **Recovery:** Wait for UTC midnight reset

### 2.4 Per-Model Concurrency Limits

**Characteristics:**

- **Scope:** Maximum simultaneous requests per model
- **Example:** z.ai: GLM-4.6 — 3 concurrent, GLM-4.7 — 2, GLM-Image — 1
- **Behavior:** Exceeding triggers 429 with cooldown; requests queued FIFO when capped
- **Recovery:** Wait for slot, or use plugin-managed queuing

---

## 3. OpenCode's Native Rate Limit Handling

### 3.1 What OpenCode CANNOT Do

| Capability | Status | Reason |
| ------------ | -------- | -------- |
| Client-side RPM throttling | ❌ Not available | OpenCode forwards requests to provider APIs without built-in rate limit awareness |
| Client-side TPM daily cap management | ❌ Not available | Daily caps are provider-enforced, not OpenCode-configurable |
| Automatic 429 backoff and retry | ❌ Not available | No post-response hook in OpenCode's plugin API |
| Per-model concurrency control | ❌ Not available | Native OpenCode has no model-level request caps |

> **Source:** `@vymalo/opencode-ratelimit` plugin README — "OpenCode has no built-in client-side rate-limit handling."

### 3.2 What OpenCode CAN Do

| Capability | Implementation | Location |
| ------------ | --------------- | ---------- |
| Provider declaration | `provider.<id>: {}` in `opencode.json` | `opencode.json` |
| Model token limits (context/output) | `limit: { context: N, output: M }` in model defs | `opencode.json` |
| Plugin-based rate limit handling | Install `opencode-concurrency-limit` or `@vymalo/opencode-ratelimit` | `opencode.json` `plugin` array |
| Subagent depth control | `subagent_depth` setting | `opencode.json` |
| Provider disabling | `"disabled": true` on model entries | `opencode.json` |

### 3.3 OpenCode Configuration Structure

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-concurrency-limit", "@vymalo/opencode-ratelimit"],
  "provider": {
    "my-provider": {
      "env": ["MY_PROVIDER_API_KEY"],
      "npm": "@ai-sdk/openai-compatible",
      "api": "https://api.my-provider.com/v1",
      "models": {
        "model-name": {
          "limit": { "context": 1000000, "output": 128000 },
          "cost": { "input": 0.1, "output": 0.2 },
          "disabled": false
        }
      }
    }
  },
  "subagent_depth": 3
}
```

---

## 4. Plugin Solutions

### 4.1 `opencode-concurrency-limit` Plugin

**Installation:**

```bash
bun add opencode-concurrency-limit
# or
npm i opencode-concurrency-limit
```

**Configuration in `opencode.json`:**

```json
{
  "plugin": ["opencode-concurrency-limit"],
  "provider": {
    "your-provider-identifier": {
      "models": {
        "your-model-name": { "options": { "concurrency": 2 } }
      }
    }
  }
}
```

**Behavior:**

- A slot is acquired right before the LLM request is sent
- A slot is released when an LLM step finishes ( `message.part.updated` with step-finish ), or on
  `session.idle / session.error` as a safety net
- While tools (Bash, Edit, etc.) are running, the slot is free — another concurrent session can start
- FIFO queue, no timeout. Requests never fail because of a busy limiter
- **Best for:** Preventing 429 errors from concurrent overload on models with hard concurrency caps

**Example — z.ai GLM models:**

```json
{
  "plugin": ["opencode-concurrency-limit"],
  "provider": {
    "zhipu": {
      "models": {
        "glm-4.6": { "options": { "concurrency": 3 } },
        "glm-4.7": { "options": { "concurrency": 2 } },
        "glm-image": { "options": { "concurrency": 1 } }
      }
    }
  }
}
```

### 4.2 `@vymalo/opencode-ratelimit` Plugin

**Installation:**

```bash
npm install @vymalo/opencode-ratelimit
```

**Configuration in `opencode.json`:**

```json
{
  "plugin": ["@vymalo/opencode-ratelimit"],
  "provider": {
    "my-provider": {
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "meta": {
          "rateLimit": {
            "enabled": true,
            "maxWaitMs": 30000,
            "maxRetries": 5,
            "headerPrefix": "x-ratelimit"
          }
        }
      }
    }
  }
}
```

**Fields:**

| Field | Default | Meaning |
| ------- | --------- | --------- |
| `enabled` | `true` | Set false to opt a provider out |
| `scope` | `model` | Keys cooldown state per (provider, model); provider shares one cooldown across whole provider |
| `maxWaitMs` | `0` | Upper bound on any single wait, in ms. 0 = unlimited (wait the full reset window) |
| `maxRetries` | `5` | How many times a 429 is retried before the response is handed back as-is |
| `headerPrefix` | `x-ratelimit` | Lowercased prefix of the draft-03 triple |
| `tiers` | — | Optional array of policy bands keyed by reset magnitude |

**Tiered policies example:**

```json
{
  "meta": {
    "rateLimit": {
      "scope": "model",
      "tiers": [
        { "maxResetSeconds": 120, "action": "wait", "maxWaitMs": 0, "maxRetries": 3 }, // ≤2min: wait it out
        { "action": "error" }                                                          // longer: surface the 429 now
      ]
    }
  }
}
```

**Pre-request gate behavior:**

1. If last response said `remaining: 0`, hold new requests until `x-ratelimit-reset` elapses
2. Send the request through the underlying fetch (or any fetch a prior plugin already installed)

**Caveats:**

- Long waits can be cut short by OpenCode's own timeouts (headerTimeout / chunkTimeout)
- With `maxWaitMs: 0`, a 55-second reset window means a 55-second wait — OpenCode may abort if it exceeds the header timeout

---

## 5. OmniRoute Alternative (If Accessible)

If you have access to OmniRoute (a more full-featured AI gateway), it provides comprehensive rate limit handling
that OpenCode lacks:

### 5.1 OmniRoute Rate Limit Features

| Feature | Configuration |
| --------- | -------------- |
| **Per-connection concurrency cap** (`max_concurrent`) | `provider_connections.max_concurrent` in dashboard/API |
| **Per-model concurrency caps** (`modelConcurrency`) | `rateLimitOverrides.modelConcurrency: { "glm-5": 1, "glm-4.7": 3 }` |
| **Quota-share serialization** | Per-connection semaphore (`qsconn:<connectionId>`) |
| **Exponential backoff** | Base delay, max delay, multiplier per provider profile |
| **Auto rate-limit protection** | Default-on for API key providers |
| **Model-specific rate limits** | Per-model concurrency caps in connection settings |
| **Environment variable tuning** | `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT`, `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS`, `OMNIROUTE_ROTATE_ON_400` |

### 5.2 OmniRoute Environment Variables

```bash
# Tuning for free-tier providers
export OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=4        # Limit concurrent heavy requests
export OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=20000     # Wait up to 20s for a slot
export OMNIROUTE_ROTATE_ON_400=true               # Skip broken models on 400/401
```

### 5.3 OmniRoute Per-Provider Rate Limit Caps (Roadmap Feature)

> **From OmniRoute issue #3152 (closed 2026-06-04):**
> "We'll add operator-configurable rate-limit caps (requests/min, concurrent requests, requests/day, tokens/day)
> per provider connection — and per-model where it makes sense — enforced proactively."
>
> **Status:** Feature tracked in backlog, not yet implemented as of v3.8.52

---

## 6. Your Specific Error: `org_token_rate_limit_day`

### 6.1 Error Analysis

**You are seeing:**

```text
org_token_rate_limit_day: Free core models share 1000000 input + output tokens per UTC day.
Enable Keep going on credits to continue, or wait for the reset. Retry after 00:00 UTC.
```

**This is NOT:**

- A per-minute RPM limit (though you may be hitting those too)
- Something OpenCode can configure directly
- A per-model token limit (OpenCode's `limit` field only controls per-request caps)

**This IS:**

- An organization-wide daily token cap for free core models
- Provider-enforced, resetting at UTC midnight
- Unaffected by OpenCode concurrency or token limit settings
- The reason your requests fail even with correct configuration

### 6.2 Immediate Workarounds

| Approach | Expected Result |
| ---------- | ---------------- |
| **Wait until UTC midnight** | All tokens reset; requests resume normally |
| **Contact provider** (Experiential Labs AI) | Request a daily limit increase if on a paid plan |
| **Upgrade to paid plan** | Higher or eliminated daily caps |
| **Use BYOK (Bring Your Own Key)** | Unaffected by organization daily caps |

### 6.3 OpenCode Configuration (Indirect Help)

While OpenCode cannot change the daily cap, these configurations help manage the **symptom**:

| Setting | How it Helps |
| --------- | ------------- |
| `opencode-concurrency-limit` plugin | Prevents concurrent request overload that could compound the daily cap issue |
| `subagent_depth: 2` (lower) | Reduces total request volume per session |
| Model `limit: { output: N }` | Prevents individual requests from consuming excessive daily tokens |
| `share: "manual"` (in opencode.json) | Prevents accidental parallel sessions that accelerate daily cap exhaustion |

**Example `opencode.json` with indirect help:**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-concurrency-limit"],
  "provider": {
    "experiential-labs": {
      "env": ["EXPERIENTIAL_LABS_API_KEY"],
      "models": {
        "your-model": {
          "limit": { "context": 100000, "output": 8192 },  // Conservative caps
          "cost": { "input": 0.01, "output": 0.02 }
        }
      }
    }
  },
  "subagent_depth": 2,
  "share": "manual"
}
```

---

## 7. Configuration Best Practices

### 7.1 OpenCode `opencode.json` Structure

**Minimum viable config for rate limit awareness:**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-concurrency-limit"],
  "provider": {
    "your-provider": {
      "env": ["YOUR_PROVIDER_API_KEY"],
      "npm": "@ai-sdk/openai-compatible",
      "api": "https://api.your-provider.com/v1",
      "models": {
        "model-you-use": {
          "limit": { "context": 1000000, "output": 128000 },
          "cost": { "input": 0.1, "output": 0.2 }
        }
      }
    }
  },
  "subagent_depth": 3
}
```

**Recommended additions for rate limit management:**

```json
{
  "plugin": ["opencode-concurrency-limit", "@vymalo/opencode-ratelimit"],
  "provider": {
    "your-provider": {
      "env": ["YOUR_PROVIDER_API_KEY"],
      "npm": "@ai-sdk/openai-compatible",
      "api": "https://api.your-provider.com/v1",
      "models": {
        "model-you-use": {
          "limit": { "context": 1000000, "output": 128000 },
          "cost": { "input": 0.1, "output": 0.2 }
        }
      },
      "options": {
        "meta": {
          "rateLimit": {
            "enabled": true,
            "maxWaitMs": 30000,
            "maxRetries": 5,
            "scope": "model"
          }
        }
      }
    }
  },
  "subagent_depth": 3,
  "share": "manual"
}
```

### 7.2 Daily Token Usage Monitoring

**Track your organization's daily token consumption:**

- Monitor how many tokens you consume per session
- Note which models/types of requests consume the most tokens
- Plan critical work around UTC midnight if near the daily limit

**Example monitoring approach:**

1. Log each request's input + output token count
2. Sum per session per UTC day
3. Alert when approaching 80% of daily limit
4. Schedule non-urgent work after UTC midnight

### 7.3 Concurrency Management

**To prevent compounding rate limit issues:**

1. **Use `opencode-concurrency-limit`** per your most-used models
2. **Set `subagent_depth` appropriately** (2-3 is typical; lower if hitting limits)
3. **Avoid parallel sessions** on the same model when near daily limits
4. **Use `share: "manual"`** to intentionally control when sessions share model access

### 7.4 Error Recovery Patterns

**When you hit a rate limit error:**

1. **Check the error type:**
   - `org_token_rate_limit_day` → Wait for UTC midnight OR contact provider
   - `429` (RPM exceeded) → Retry with exponential backoff, consider concurrency limits
   - `400/401` (broken model) → Use `OMNIROUTE_ROTATE_ON_400` or switch models

2. **Apply appropriate recovery:**
   - Daily cap: Wait until next UTC midnight
   - RPM: Wait 60s / use backoff, or configure `opencode-concurrency-limit`
   - Model issues: Switch models, check credentials

3. **Log the error** for pattern analysis:
   - Note which model triggered the error
   - Record timestamp and context
   - Track frequency over time

---

## 8. Folder Structure & File Conventions

### 8.1 Documentation Location

This guide follows the project's documentation conventions:

| Directory | Convention | Example |
| ----------- | ---------- | --------- |
| `docs/` | `YYYY-MM-DD-title.md` format | `docs/2026-07-03_<session-id>_<topic>_task.md` |
| `docs/guides/opencode/investigations/<date>-<topic>/` | Dated case folders with `README.md`, `AGENTS.md`, `sources.md` | `2026-11-15-opencode-rate-limit-handling/` |
| `.agents/skills/<name>/SKILL.md` | Skill documentation | `.agents/skills/opencode-provider-persistence-config/SKILL.md` |
| `AGENTS.md` (root) | DOX hierarchy with Child DOX Index | Root AGENTS.md |

### 8.2 Closeout & DOX Compliance

**Per AGENTS.md closeout procedure:**

1. ✅ **Re-check changed paths against DOX chain** - This doc is placed under the owning investigation folder
2. ✅ **Update nearest owning AGENTS.md** - The investigation folder's `AGENTS.md` lists this companion document
3. ✅ **Refresh every affected Child DOX Index** - `docs/guides/opencode/AGENTS.md` is accurate; the folder `AGENTS.md`
   enumerates the four documents it owns
4. ✅ **Remove stale or contradictory text** - N/A (new doc, no stale content)
5. ⚠️ **Run existing verification when relevant** - Verify the doc content is accurate against current OpenCode version

**DOX Chain Check:**

- Root: `AGENTS.md` ← No conflict
- `docs/AGENTS.md` ← No conflict (owning folder updated)
- Child: `docs/guides/opencode/AGENTS.md` ← Investigation already indexed there
- Format: Follows dated investigation folder convention ✅

### 8.3 Related Docs in Repository

| Doc | Purpose | Relation |
| --- | --- | --- |
| [`README.md`](README.md) | Owning incident analysis | Complementary operational view |
| [`platform-facts.md`](../../../../../mom-automation/docs/research/platform-facts.md) | Fireflies/Gemini/Notion limits | Different providers |

---

## 9. Version History

| Version | Date | Changes | Author |
| ------- | ---- | ------- | ------ |
| 1.0 | 2026-11-15 | Initial release | OpenCode Agent |

---

## 10. Contact & Support

- **Provider:** Experiential Labs AI (for daily cap increases)
- **OpenCode Issues:** <https://github.com/anomalyco/opencode/issues>
- **OmniRoute Docs:** <https://github.com/diegosouzapw/OmniRoute>
- **Plugin Repos:**
    - `opencode-concurrency-limit`: <https://github.com/loss-and-quick/opencode-concurrency-limit>
    - `@vymalo/opencode-ratelimit`: <https://www.npmjs.com/package/@vymalo/opencode-ratelimit>

---
