# `verify-ingest.py.md` — Explainer (Industrial Explainer Pattern 1.4)

## Deep Technical Breakdown

| Logic | Rationale |
|---|---|
| `api_get` returns `(status, body)` instead of raising on HTTP errors | Verification must distinguish 404 (unknown object) from 403 (Anubis) from 200 — each maps to a different verdict. Transport errors (DNS, timeout) raise `RuntimeError` and become FAILED exit 2. |
| Three-stage check: `origin/get` → `revision/<sha>` → `visit/latest` + snapshot branch scan | The revision endpoint alone is insufficient: a commit can be archived via another origin. The snapshot branch scan comparing `target.lower() == expected` across ALL branches proves *this origin's* crawl captured the push. |
| `require_snapshot=true` query on `visit/latest` | Without this flag, the latest visit may return without a snapshot (ongoing), causing a spurious PENDING. |
| Exit 0/1/2 → VERIFIED/PENDING/FAILED | PENDING (origin known, HEAD not yet snapshotted) is ingest lag, not breakage — CI warns instead of failing so `main` never goes red between SWH crawler runs. |
| `--trigger-save` POSTs `data=b""` with `method="POST"` | `urllib` sends GET unless `data` is set; empty body reproduces the Save button's call. Best-effort by design. |

## Common Use Cases
- CI: two `--check` flags (superproject HEAD + submodule SHA), `--json` for log parsing.
- Local: `--trigger-save` followed by re-check after save completes.

## Edge Cases
- HTTP 403 → reported with Anubis hint, verdict FAILED (exit 2).
- `visit/latest` with no snapshot yet → falls through to PENDING.
- Malformed `--check` (no comma) → exit 2 with usage error before any network call.

## Recommended Enhancements
- Persist per-origin visit_date/snapshot id to a state file and annotate the PR.
- Add `--wait --interval` polling mode that blocks until VERIFIED or a deadline.
