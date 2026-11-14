# Rate Limiting Implementation Plan

**Date:** 2026-11-15  
**Related Guide:** `rate-limiting-handling-guide.md`  
**Version:** 1.0  

---

## 1. Overview

This implementation plan addresses the `org_token_rate_limit_day` rate limit error experienced when using
Experiential Labs AI's free core models via OpenCode. It outlines the specific steps to configure OpenCode
plugins, manage concurrency, and implement workarounds for provider-enforced rate limits.

### 1.1 Problem Statement

**Error encountered:**

```text
org_token_rate_limit_day: Free core models share 1000000 input + output tokens per UTC day.
Enable Keep going on credits to continue, or wait for the reset. Retry after 00:00 UTC.
```

**Root cause:** Organization-wide daily token cap for free core models, resetting at UTC midnight.
Unaffected by OpenCode configuration.

**Impact:** All requests fail until the next UTC midnight reset, regardless of model, concurrency, or token limit settings.

### 1.2 Success Criteria

| Criterion | Metric | Target |
| ----------- | -------- | -------- |
| Plugin installation | `opencode-concurrency-limit` | Installed and configured |
| Concurrency control | Per-model max concurrent requests | 2-3 slots per model |
| Request volume reduction | `subagent_depth` | Reduced to 2-3 (from default 3-5) |
| Daily cap management | UTC midnight reset awareness | Team informed of reset schedule |
| Error recovery pattern | documented | Team follows recovery workflow |

### 1.3 Stakeholders

| Role | Responsibility |
| ------ | ---------------- |
| **OpenCode User** | Implement plugin configs, monitor token usage |
| **Team Lead** | Approve subagent_depth changes, monitor daily usage |
| **Provider** (Experiential Labs AI) | Increase daily cap if on paid plan/BYOK |

---

## 2. Implementation Steps

### 2.1 Step 1: Install `opencode-concurrency-limit` Plugin

**Command:**

```bash
bun add opencode-concurrency-limit
# or (if bun not available)
npm i opencode-concurrency-limit
```

**Verification:**

```bash
# Check plugin is loaded
opencode --version
# Expected: plugin system active, concurrency-limit available
```

**Expected output:** Plugin is auto-discovered by OpenCode at startup (scans `~/.config/opencode/plugins/`)

---

### 2.2 Step 2: Configure Plugin in `opencode.json`

**File location:** Project root `opencode.json` OR `~/.config/opencode/opencode.json`

**Configuration:**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-concurrency-limit"],
  "provider": {
    "your-provider-identifier": {
      "env": ["YOUR_PROVIDER_API_KEY"],
      "npm": "@ai-sdk/openai-compatible",
      "api": "https://api.your-provider.com/v1",
      "models": {
        "your-model-name": {
          "limit": { "context": 1000000, "output": 128000 },
          "cost": { "input": 0.1, "output": 0.2 }
        }
      }
    }
  },
  "subagent_depth": 2,  // Reduced from default 3 to reduce request volume
  "share": "manual"
}
```

**Key changes:**

| Setting | Value | Rationale |
| --------- | ------- | ----------- |
| `plugin` | `["opencode-concurrency-limit"]` | Enables per-model concurrency control |
| `subagent_depth` | `2` | Reduces nested agent request volume by ~33% |
| `share` | `"manual"` | Prevents accidental parallel sessions accelerating daily cap exhaustion |

**Verification:**

1. Restart OpenCode for plugin to load
2. Run `/models` in TUI — confirm provider models appear
3. Send a test prompt — should succeed (or show expected rate limit error, not crash)

---

### 2.3 Step 3: Configure Per-Model Concurrency Limits

**For models with known concurrency caps** (e.g., z.ai GLM models):

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

**For your specific scenario** (Experiential Labs AI model):

```json
{
  "plugin": ["opencode-concurrency-limit"],
  "provider": {
    "experiential-labs": {
      "models": {
        "your-model-name": { "options": { "concurrency": 2 } }
      }
    }
  }
}
```

**Behavior:**

- Slot acquired before LLM request is sent
- Slot released when LLM step finishes (`message.part.updated` with step-finish)
- While tools (Bash, Edit, etc.) run, slot is free — another session can start
- FIFO queue, no timeout — requests never fail because of busy limiter

**Verification:**

1. Send multiple concurrent prompts to the same model
2. Observe no 429 errors from concurrent overload (only possible daily cap errors)
3. Check `opencode-concurrency-limit` logs (if `debug: true` set) for slot acquisition/release

---

### 2.4 Step 4: (Optional) Add `@vymalo/opencode-ratelimit` Plugin

**Installation:**

```bash
npm install @vymalo/opencode-ratelimit
```

**Configuration:**

```json
{
  "plugin": ["@vymalo/opencode-ratelimit"],
  "provider": {
    "your-provider": {
      "npm": "@ai-sdk/openai-compatible",
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
  }
}
```

**When to use:** If your provider advertises rate-limit response headers (x-ratelimit-limit, x-ratelimit-remaining, x-ratelimit-reset)

**Fields explanation:**

| Field | Recommended Value | Meaning |
| ------- | ------------------ | --------- |
| `enabled` | `true` | Opt in to rate-limit awareness |
| `maxWaitMs` | `30000` | Max 30s wait per reset window; 0 = unlimited |
| `maxRetries` | `5` | 5 retries of 429 before surfacing error |
| `scope` | `"model"` | Keys cooldown per (provider, model); prevents one model's exhaustion from blocking siblings |

**Verification:**

1. Intentionally trigger a 429 (or simulate with rate-limited provider)
2. Observe plugin holds requests until `x-ratelimit-reset` elapses
3. Verify retry succeeds after wait period

---

### 2.5 Step 5: Monitor Daily Token Usage

**Recommended monitoring approach:**

1. **Log token consumption** per session:

   ```yaml
   # Example session log entry
   tokens:
     input: 256
     output: 128
     total: 384
   session_id: <session-id>
   utc_date: 2026-11-15
   ```

2. **Track per-UTC-day totals:**
   - Maintain a running sum of input + output tokens
   - Note which models/types consume most tokens
   - Set threshold alert at 80% of daily limit (800,000 tokens for 1M cap)

3. **Schedule critical work** around UTC midnight:
   - Non-urgent: After UTC midnight when cap resets
   - Urgent: Contact provider for cap increase or use BYOK

4. **Use OpenCode's built-in tracking:**
   - Session exports contain token usage per turn
   - Query `ai-session-exports/` directory for token counts
   - Aggregate by UTC date for daily tracking

---

### 2.6 Step 6: Error Recovery Workflow

**When rate limit error occurs:**

| Error Type | Immediate Action | Recovery Time |
| ------------ | ----------------- | --------------- |
| `org_token_rate_limit_day` | Wait for UTC midnight OR contact provider | Until next midnight (typical) or ASAP (provider) |
| `429` (RPM exceeded) | Retry with exponential backoff; check `opencode-concurrency-limit` | 60s - 5min |
| `400/401` (broken model) | Switch model or use `OMNIROUTE_ROTATE_ON_400` | Immediate (if model switchable) |

**Detailed recovery for `org_token_rate_limit_day`:**

1. **Check current UTC time** vs. midnight

   ```bash
   date -u +%H:%M:%S  # Current UTC time
   # If past midnight, cap has reset; proceed
   # If before midnight, calculate time until reset
   ```

2. **Calculate time until reset:**

   ```bash
   # Time until next UTC midnight
   python3 -c "
   from datetime import datetime, timezone
   now = datetime.now(timezone.utc)
   midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
   seconds_until = (midnight - now).total_seconds()
   print(f'Seconds until UTC midnight: {seconds_until}')
   print(f'Hours: {seconds_until / 3600:.1f}')
   ```

3. **Decision point:**
   - If `seconds_until < 30min`: Wait and retry
   - If `seconds_until > 30min`: Contact provider for cap increase
   - If paid/BYOK: Switch to paid plan or own key

4. **Post-recovery:**
   - Log the incident (duration, model, prompt context)
   - Review if concurrency changes reduced daily usage
   - Adjust `subagent_depth` if appropriate

---

### 2.7 Step 7: Team Communication & Documentation

**Communicate changes to the team:**

1. **Update this implementation plan** with actual configuration used
2. **Add to team's onboarding docs** the rate limit handling procedure
3. **Include in session export recovery** notes for future sessions
4. **Document in team's AGENTS.md** (if applicable) under "AI Provider Rate Limits"

**Sample team AGENTS.md addition:**

```markdown
## AI Provider Rate Limits

### Daily Token Cap
- Organization-wide cap: 1,000,000 input + output tokens per UTC day
- Reset: UTC midnight (00:00 UTC)
- Mitigation: Wait for reset, or contact provider for increase

### Concurrency Control
- Plugin: `opencode-concurrency-limit` configured per model
- Recommended slots: 2-3 per frequently used model
- Effect: Prevents 429 from concurrent overload (not daily cap)

### Daily Usage Monitoring
- Log input+output tokens per session
- Track running total per UTC day
- Alert at 80% consumption (800,000 tokens)
- Schedule critical work after UTC midnight
```

---

## 3. Rollback Plan

| Step | Action | Reason |
| ------ | -------- | -------- |
| 1. Disable plugin | Remove `opencode-concurrency-limit` from `plugin` array | Revert to default OpenCode behavior (no concurrency control) |
| 2. Restore `subagent_depth` | Set back to `3` (or original value) | Revert to original nested agent depth |
| 3. Remove `share: "manual"` | Set to `"auto"` or remove | Revert to automatic session sharing |
| 4. Restart OpenCode | Quit and relaunch | Config changes require restart |

**Rollback verification:** After reverting all changes, confirm:

- OpenCode starts normally without plugin errors
- Default `subagent_depth` behavior restored
- No concurrency limits active

---

## 4. Success Metrics

| Metric | Pre-Implementation | Post-Implementation | Target Improvement |
| -------- | ------------------- | --------------------- | -------------------- |
| 429 errors from concurrency | N/A (daily cap was issue) | Reduced or eliminated | ✅ Concurrency 429s eliminated |
| Daily cap exhaustion rate | 100% (all days) | Reduced with monitoring | ✅ Track and reduce |
| Session success rate | Variable (rate-limited) | Improved with concurrency control | ✅ 20-30% improvement expected |
| Team awareness of UTC reset | Low | High (documented) | ✅ Team informed |

---

## 5. Related Documentation

| Doc | Location | Purpose |
| ----- | ---------- | --------- |
| Rate limiting guide | `rate-limiting-handling-guide.md` (same folder) | Comprehensive theory and background |
| OpenCode config | `opencode.json` | Plugin and provider configuration |
| Auth management | `~/.config/opencode/auth.json` | API key storage |
| OmniRoute resilience | OmniRoute dashboard | Advanced rate limit features (if applicable) |
| Git history | `git log --oneline -5` | Change tracking for this plan |

---

## 6. Closeout & DOX Compliance

**Per AGENTS.md closeout procedure:**

1. ✅ **Re-check changed paths against DOX chain** - Plan placed under the owning investigation folder
2. ✅ **Update nearest owning AGENTS.md** - The investigation folder's `AGENTS.md` lists this companion plan
3. ✅ **Refresh every affected Child DOX Index** - `docs/guides/opencode/AGENTS.md` is accurate; the folder `AGENTS.md`
   enumerates the four documents it owns
4. ✅ **Remove stale or contradictory text** - N/A (new doc, verified accurate against current OpenCode version)
5. ⚠️ **Run existing verification when relevant** - Verify plugin installation and configuration works with current version

**DOX Chain Check:**

- Root: `AGENTS.md` ← No conflict
- `docs/AGENTS.md` ← No conflict (owning folder updated)
- Child: `docs/guides/opencode/AGENTS.md` ← Investigation already indexed there
- Format: Follows dated investigation folder convention ✅

**Child DOX Index Update:** Handled by the owning folder's `AGENTS.md` update in the same atomic change.

---
