# NVIDIA build.nvidia.com Free 1M Context Models - Sorted by Input/Output Length

Complete list of **5 free endpoint models** with 1M context, sorted by output token capacity.

**Free Tier Limits:**
- Credits on signup: 1,000 (up to 5,000)
- Rate limit: 40 requests/min
- Credit card: Not required
- Source: https://build.nvidia.com/models?filters=nimType%3Anim_type_preview

---

## 1M Context Models (Sorted by Output Capacity)

| Rank | Model ID | Provider | Total Params | Active Params | Context (Input) | Max Output | Best For |
|------|----------|----------|--------------|---------------|-----------------|------------|----------|
| 1 | `deepseek-v4-pro` | DeepSeek | 1.6T | 49B | 1,000,000 | 384,000 | Coding, long-form generation |
| 2 | `deepseek-v4-flash` | DeepSeek | 284B | 13B | 1,000,000 | 384,000 | Fast coding, agents |
| 3 | `nemotron-3-ultra-550b-a55b` | NVIDIA | 550B | 55B | 1,000,000 | 32,768 | Frontier reasoning, agentic |
| 4 | `nemotron-3-super-120b-a12b` | NVIDIA | 120B | 12B | 1,000,000 | 32,768 | Agentic coding, tool calling |
| 5 | `nemotron-3-nano-30b-a3b` | NVIDIA | 30B | 3B | 1,000,000 | 32,768 | Efficient coding, instruction following |

---

## Detailed Comparison

### Input Capacity (All equal: 1M tokens)

| Model | Input Tokens | Equivalent |
|-------|--------------|------------|
| All 5 models | 1,000,000 | ~750,000 English words or ~1.65M Chinese characters |

### Output Capacity (Different)

| Model | Max Output Tokens | Equivalent |
|-------|-------------------|------------|
| deepseek-v4-pro | 384,000 | ~288,000 English words |
| deepseek-v4-flash | 384,000 | ~288,000 English words |
| nemotron-3-ultra-550b-a55b | 32,768 | ~24,500 English words |
| nemotron-3-super-120b-a12b | 32,768 | ~24,500 English words |
| nemotron-3-nano-30b-a3b | 32,768 | ~24,500 English words |

### Model Efficiency (Active Parameters)

| Model | Total Params | Active Params | Efficiency |
|-------|--------------|---------------|------------|
| nemotron-3-nano-30b-a3b | 30B | 3B | 10% (most efficient) |
| nemotron-3-super-120b-a12b | 120B | 12B | 10% |
| deepseek-v4-flash | 284B | 13B | 4.6% |
| nemotron-3-ultra-550b-a55b | 550B | 55B | 10% |
| deepseek-v4-pro | 1.6T | 49B | 3.1% |

### Reasoning Modes

| Model | Thinking Mode | Configurable |
|-------|---------------|--------------|
| deepseek-v4-pro | non-thinking / high / max | Yes |
| deepseek-v4-flash | non-thinking / high / max | Yes |
| nemotron-3-ultra-550b-a55b | enable_thinking=True/False | Yes |
| nemotron-3-super-120b-a12b | enable_thinking=True/False | Yes |
| nemotron-3-nano-30b-a3b | enable_thinking=True/False | Yes |

### Supported Languages

| Model | Languages |
|-------|-----------|
| deepseek-v4-pro | Multilingual |
| deepseek-v4-flash | Multilingual |
| nemotron-3-ultra-550b-a55b | English, French, Spanish, Italian, German, Japanese, Korean, Hindi, Brazilian Portuguese, Chinese |
| nemotron-3-super-120b-a12b | English, French, German, Italian, Japanese, Spanish, Chinese |
| nemotron-3-nano-30b-a3b | English (+ multilingual) |

---

## Recommendations

### For Coding with Large Outputs
**Best choice: `deepseek-v4-pro`** or **`deepseek-v4-flash`**
- 384k output tokens (12x more than Nemotron)
- Perfect for generating large code files, documentation, or refactoring entire codebases

### For Agentic Workflows
**Best choice: `nemotron-3-super-120b-a12b`**
- Optimized for tool calling and agentic reasoning
- 1M context for large codebases
- 32k output sufficient for most agent tasks

### For Efficiency (Low Resource Usage)
**Best choice: `nemotron-3-nano-30b-a3b`**
- Only 3B active parameters (most efficient)
- 1M context still available
- Fastest inference

### For Maximum Capability
**Best choice: `nemotron-3-ultra-550b-a55b`**
- Most capable Nemotron model
- 55B active parameters
- Best reasoning and multilingual support

---

## Quick Reference

| Use Case | Recommended Model | Why |
|----------|-------------------|-----|
| Generate large code files | deepseek-v4-pro | 384k output |
| Fast coding assistance | deepseek-v4-flash | 384k output, faster |
| Build AI agents | nemotron-3-super-120b-a12b | Optimized for tool calling |
| Budget/resource constrained | nemotron-3-nano-30b-a3b | 3B active, most efficient |
| Complex reasoning | nemotron-3-ultra-550b-a55b | Most capable |
