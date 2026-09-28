#!/usr/bin/env bash
set -euo pipefail

REQUEST_FILE="${1:-scratch/vercel-curl-request.json}"
MODEL="${2:-voyage/voyage-code-3}"
RESPONSE_FILE="${3:-scratch/vercel-symbol-curl-response.json}"
HEADER_FILE="${4:-scratch/vercel-symbol-curl-headers.txt}"

: "${AI_GATEWAY_API_KEY:?AI_GATEWAY_API_KEY must be set}"
command -v jq >/dev/null || { echo "error: jq is required" >&2; exit 1; }

mkdir -p "$(dirname "$RESPONSE_FILE")" "$(dirname "$HEADER_FILE")"

jq '.body
  | .prompt = [
      {"role":"system","content":"You are a code symbol inspector. Reply with only the symbol signature."},
      {"role":"user","content":[{"type":"text","text":"Inspect this symbol: add(a, b) = a + b. Reply with the symbol signature only."}]}
    ]
  | .maxOutputTokens = 64
  | .temperature = 0
  | .providerOptions = {}
  | .includeRawChunks = false' "$REQUEST_FILE" |
  curl --silent --show-error --location --max-time 60 \
    -D "$HEADER_FILE" \
    -o "$RESPONSE_FILE" \
    -w 'http_status=%{http_code}\n' \
    -X POST 'https://ai-gateway.vercel.sh/v3/ai/language-model' \
    -H "Authorization: Bearer ${AI_GATEWAY_API_KEY}" \
    -H 'Content-Type: application/json' \
    -H 'User-Agent: curl/opencode-symbol-probe' \
    -H 'ai-gateway-auth-method: api-key' \
    -H 'ai-gateway-protocol-version: 0.0.1' \
    -H "ai-language-model-id: ${MODEL}" \
    -H 'ai-language-model-specification-version: 3' \
    -H 'ai-language-model-streaming: false' \
    -H 'http-referer: https://opencode.ai/' \
    -H 'x-session-id: curl-symbol-probe' \
    -H 'x-title: opencode' \
    --data-binary @-
