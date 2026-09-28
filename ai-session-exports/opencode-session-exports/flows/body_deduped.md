# OpenCode Zen Stream — Laguna S 2.1 Free

## Metadata

- **ID**: `gen-1784672149-hny12TxoiSkP8VuFs5bW`
- **Object**: chat.completion.chunk
- **Created**: 1784672149 (2026-07-22T03:45:49)
- **Model**: laguna-s-2.1-free

## SSE Comments

### Processing (5×)

- `OPENROUTER PROCESSING`
- `OPENROUTER PROCESSING`
- `OPENROUTER PROCESSING`
- `OPENROUTER PROCESSING`
- `OPENROUTER PROCESSING`

### Keep-Alive (4×)

- `keep-alive`
- `keep-alive`
- `keep-alive`
- `keep-alive`

## Reasoning

The user wants a curl command to test the Laguna S 2.1 Free model. I need to construct a curl command that hits the OpenCode Zen API endpoint. Let me think about what's needed:

1. The endpoint is `https://opencode.ai/zen/v1/chat/completions`
2. It uses OpenAI-compatible API format
3. The model ID is `laguna-s-2.1-free`
4. It requires an API key for authentication

I should provide a curl command that the user can use to test the model. I'll need to include a placeholder for the API key and a simple test prompt.

## Response

Here's a curl command to test the Laguna S 2.1 Free model:

```bash
curl https://opencode.ai/zen/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <redacted-auth-header>" \
  -d '{
    "model": "laguna-s-2.1-free",
    "messages": [
      {"role": "user", "content": "Write a simple Python function to calculate the Fibonacci sequence."}
    ],
    "max_tokens": 512,
    "temperature": 0.7
  }'
```

Replace `<redacted-auth-header>` with your actual OpenCode Zen API key. You can get one by signing in at [OpenCode Zen](https://opencode.ai/auth).

For streaming responses, add `"stream": true` to the request body.

## Usage

| Metric | Value |
|--------|-------|
| Prompt tokens | 75,341 |
| Completion tokens | 326 |
| Total tokens | 75,667 |
| Cached tokens | 1,856 |
| Reasoning tokens | 134 |

## Cost

- **Type**: inference-cost
- **Cost**: $0.00000000
- **Input tokens**: 73,485
- **Output tokens**: 326
- **Reasoning tokens**: 134
- **Cache read tokens**: 1,856
- **Reasoning mode**: effort
- **Reasoning effort**: high

## End

```
[DONE]
```

---
*Generated from `body_deduped.yaml`*