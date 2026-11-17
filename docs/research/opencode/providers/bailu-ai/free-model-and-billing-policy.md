<!-- title: Bailu verified-free labeling, quota billing, and OpenCode visibility policy -->

# Free Models, Billing, and Visibility

## What Free Means

Free means verified access without monetary payment under the current account/key policy.
It does not mean zero token usage, a missing price estimate, or the word `free` appearing in an ID.

The authenticated account meter reported 796,500,000 effective token allowance, with an active key fingerprint
matching the persisted OpenCode key. The key's prior usage was 6,481,462 tokens with `total_price: 0`.
The balance/recharge UI was marked “SOON”. Before/after key-price checks and the per-request token records qualify
the quota-only audit; no top-up, subscription, or paid fallback was used.

The matched key counter rose from 6,481,462 to 14,067,572 tokens (7,586,110) and from 188 to 370 requests.
Captured direct/OpenCode response events account for 146,421 raw tokens; the remaining 7,439,689-token difference
is not fully attributable from the available provider/client evidence. Possible contributors include provider/internal
retries, cache/accounting semantics, concurrent matched-key use, or usage omitted from response events.
Recorded coefficient-weighted request usage was 127,712.8 units, but it is not a substitute for aggregate meter parity.
No further inference was run after identifying the discrepancy. Monetary price remained zero.

`billing_coefficient` is a token-quota multiplier, not a USD-per-token monetary rate. Native per-call/per-second
units also cannot become a text-token cost estimate. Unknown monetary prices remain absent in the config.

## Naming

1. Use the API-provided model name if present and usable; otherwise the exact ID.
2. Add one literal suffix `" (free)"` only for confirmed-free access.
3. Normalize repeated/case-varied annotation markers; preserve exact IDs and non-annotation name content.
4. Do not generate, prettify, or infer a model name. `cost` never determines the free annotation.

## Visibility

An admitted model must have current free access, complete direct text/SSE/tool/result outcomes, intended OpenCode
reply/read-tool success, and a complete saved-routing result. Payment, non-chat, down/blocked, malformed/incomplete,
failed required capability, and unverified cases remain blacklisted.

The [policy CSV](evidence/model-policy.csv) retains all 60 IDs, names, evidence, and reasons.
The [portable provider payload](evidence/provider-payload-free-only.jsonc) contains no credentials.
