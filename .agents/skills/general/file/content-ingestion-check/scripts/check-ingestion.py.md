# `check-ingestion.py.md` — Explainer (Industrial Explainer Pattern 1.4)

## Deep Technical Breakdown

| Logic | Rationale |
|---|---|
| `http_get` raises `RuntimeError` on HTTP 403 but returns `(status, body)` for other HTTP errors | A 403 from SWH is the Anubis PoW challenge — that's an environment blocker (the operator must solve the PoW once in a browser), not an "unknown content" verdict. Other 4xx/5xx are returned as status codes so the caller can distinguish 404 (unknown content) from 500 (server error). |
| `--hash` (single) vs `--hashes <file>` (batch) are mutually exclusive | Single-check mode is for interactive use (one file just hashed by `git-blob-hash`); batch mode is for the content-link minter emitting dozens of links. The batch path uses SWH's `content/known/` endpoint, but falls back to per-hash single lookups if the endpoint shape differs. |
| `exit 0/1/2 = all known / any unknown / transport error` | Mirrors the convention used by the pre-commit verification protocol. Exit 1 (some unknown) is a "wait" signal, not a failure — content may be ingested after a Save request. |
| `USER_AGENT` includes the ai-suite repo URL | SWH operators can attribute verification traffic; also satisfies SWH's robots-friendly client guidance. |

## Common Use Cases

- Gate SWH link emission: `check-ingestion.py --hash <sha> && emit_link`.
- Bulk-verify a tree's hashes after a Save-code-now submission.
- Adapt to IPFS: `--api-base https://ipfs.io/api/v0 --single-path /repo/cat?arg={hash}` (returns different shapes, but the known/unknown verdict pattern holds).

## Edge Cases

- **Batch with 1 result unknown, 9 known**: exit 1; JSON shows which is missing.
- **Malformed `--hashes` file (lines > 40 chars or non-hex)**: silently skipped via `len(h)==40` filter.
- **Archive returns 200 with empty body (non-JSON)**: `json.JSONDecodeError` caught; status returned as 200 but `known=false` path.

## Recommended Enhancements

- Add `--wait` polling mode that re-checks every N seconds up to a deadline.
- Support `sha256` and `blake2s256` hash types (SWH indexes all three).
