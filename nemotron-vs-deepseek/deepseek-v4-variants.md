# DeepSeek V4 Variants Comparison

DeepSeek V4 has **2 models** x **3 reasoning modes** = **6 total variants**.

---

## Model Comparison

| Feature | V4-Pro | V4-Flash |
|---------|--------|----------|
| **Total Parameters** | 1.6 Trillion | 284 Billion |
| **Active Parameters** | 49 Billion | 13 Billion |
| **Context Window** | 1M tokens | 1M tokens |
| **Max Output** | 384,000 tokens | 384,000 tokens |
| **Weight Size** | ~862GB | ~158GB |
| **License** | MIT | MIT |
| **Release Date** | April 23, 2026 | April 23, 2026 |

---

## Reasoning Modes (Both Models)

| Mode | Speed | Accuracy | Best For |
|------|-------|----------|----------|
| **Non-think** | Fastest | Good | Simple tasks, chat |
| **High** | Medium | Better | Complex problem-solving |
| **Max** | Slowest | Best | Competitive programming, math proofs |

---

## Benchmarks

### V4-Pro

| Benchmark | Non-think | High | Max |
|-----------|-----------|------|-----|
| **MMLU-Pro** | 82.9 | 87.1 | **87.5** |
| **GPQA Diamond** | 72.9 | 89.1 | **90.1** |
| **LiveCodeBench** | 56.8 | 89.8 | **93.5** |
| **SWE-Bench Verified** | 73.6 | 79.4 | **80.6** |
| **Terminal Bench 2.0** | 59.1 | 63.3 | **67.9** |
| **HLE (no tools)** | 7.7 | 34.5 | **37.7** |
| **Codeforces Rating** | - | 2919 | **3206** |

### V4-Flash

| Benchmark | Non-think | High | Max |
|-----------|-----------|------|-----|
| **MMLU-Pro** | 83.0 | 86.4 | 86.2 |
| **GPQA Diamond** | 71.2 | 87.4 | 88.1 |
| **LiveCodeBench** | 55.2 | 88.4 | **91.6** |
| **SWE-Bench Verified** | 73.7 | 78.6 | 79.0 |
| **Terminal Bench 2.0** | 49.1 | 56.6 | 56.9 |
| **HLE (no tools)** | 8.1 | 29.4 | 34.8 |
| **Codeforces Rating** | - | 2816 | 3052 |

---

## V4-Pro vs V4-Flash (Max Mode)

| Benchmark | V4-Pro | V4-Flash | Winner |
|-----------|--------|----------|--------|
| **MMLU-Pro** | **87.5** | 86.2 | V4-Pro |
| **GPQA Diamond** | **90.1** | 88.1 | V4-Pro |
| **LiveCodeBench** | **93.5** | 91.6 | V4-Pro |
| **SWE-Bench Verified** | **80.6** | 79.0 | V4-Pro |
| **Terminal Bench 2.0** | **67.9** | 56.9 | V4-Pro |
| **HLE (no tools)** | **37.7** | 34.8 | V4-Pro |
| **Codeforces Rating** | **3206** | 3052 | V4-Pro |

**Winner: V4-Pro** (leads by 1-11 points)

---

## Pricing (DeepSeek API)

| Metric | V4-Pro | V4-Flash |
|--------|--------|----------|
| **Input (cache hit)** | $0.145/1M | $0.028/1M |
| **Input (cache miss)** | $1.74/1M | $0.14/1M |
| **Output** | $3.48/1M | $0.28/1M |

**V4-Flash is 12x cheaper** on output tokens.

---

## NVIDIA build.nvidia.com (Free)

| Model | Available |
|-------|-----------|
| `deepseek-v4-pro` | Free endpoint |
| `deepseek-v4-flash` | Free endpoint |

**Both are free** on NVIDIA's API.

---

## When to Use Each

### V4-Pro (Max)

| Use Case | Why |
|----------|-----|
| **Competitive programming** | Highest scores (3206 rating) |
| **Math proofs** | Best reasoning (90.1 GPQA) |
| **Multi-file refactoring** | Best coding (80.6% SWE-Bench) |
| **Complex agentic workflows** | Best agentic (67.9% Terminal Bench) |
| **Large codebase generation** | 384k output tokens |

### V4-Flash (Max)

| Use Case | Why |
|----------|-----|
| **Simple code completion** | Fast, cheap |
| **Chat and Q&A** | Good enough quality |
| **Document analysis** | 1M context, cheaper |
| **High-volume production** | 12x cheaper |
| **Self-hosting** | 158GB vs 862GB |

### Non-think Mode (Either Model)

| Use Case | Why |
|----------|-----|
| **Quick questions** | Fastest response |
| **Simple bug fixes** | Good enough |
| **Code completion** | Low latency |

---

## Recommendation for OpenCode

**Best choice: `deepseek-v4-pro` (Max mode)**

Why:
1. **Highest benchmarks** - 87.5 MMLU, 90.1 GPQA, 93.5 LiveCodeBench
2. **Best coding** - 80.6% SWE-Bench
3. **Best agentic** - 67.9% Terminal Bench
4. **384k output** - Generate entire codebases
5. **Free on NVIDIA** - No cost

**Use `deepseek-v4-flash` if:**
- You need faster responses
- You're doing simple tasks
- You want to self-host

---

## Quick Reference

| You Need | Use This |
|----------|----------|
| Best quality | `deepseek-v4-pro` Max |
| Fast responses | `deepseek-v4-pro` Non-think |
| Simple tasks | `deepseek-v4-flash` Non-think |
| Cheap production | `deepseek-v4-flash` Max |
| Free API | `deepseek-v4-pro` on NVIDIA |
