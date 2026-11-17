<!-- title: Cache-aware NVIDIA NIM OpenCode supplement refresh and verification -->

# Refresh and Verify the NVIDIA Supplement

Runtime source is `opencode/config/scripts/sync-nvidia-nim-models.py` in the configuration repository.
It uses ai-suite's existing JSONC CST parser and ships independent offline tests and a technical explainer.
The config remains the user's global OpenCode configuration; the cache and auth are read-only inputs.

## Workflow

1. Capture a fresh baseline runtime list with `opencode models nvidia`, before collecting new supplement state.
2. Run `collect` to save authenticated API IDs, the current NVIDIA cache layer, and protected config/auth hashes.
3. Run `metadata` to acquire hosted references/cards only for API IDs absent from that cached layer.
4. Run `sync` without `--apply` to emit the provider fragment, full isolated config, complete patch, and ownership report.
5. Verify that candidate runtime equals the baseline plus generated missing IDs and inspect the complete patch.
6. Apply with both reviewed current config/cache SHA-256 values; retain the protected config preimage.
7. Run `verify` and publish portable research evidence. Restart existing OpenCode instances to load the new config.

Command template; `WORK`, config, cache, auth, and OpenCode paths are explicit caller-owned parameters:

```bash
python3 sync-nvidia-nim-models.py collect --out "$WORK"
python3 sync-nvidia-nim-models.py metadata --out "$WORK"
python3 sync-nvidia-nim-models.py sync --out "$WORK" --ai-suite-root "$AI_SUITE"
python3 sync-nvidia-nim-models.py sync --out "$WORK" --ai-suite-root "$AI_SUITE" \
  --apply --expected-config-sha256 "$CONFIG_SHA256" --expected-cache-sha256 "$CACHE_SHA256"
python3 sync-nvidia-nim-models.py verify --out "$WORK" --ai-suite-root "$AI_SUITE" \
  --opencode "$OPENCODE" --baseline-runtime "$BASELINE_RUNTIME"
```

Subsequent refreshes automatically read `nvidia-nim-supplement-ownership.json` beside the resolved config.
The [portable ownership report](evidence/supplement-ownership.json) mirrors the managed definitions for review;
`--previous-report` remains an optional conflict-checked import, not the persistent SSOT.
If cache coverage grows, only unchanged generated overlaps are retired. Catalog disappearance is reported without
deletion, and user drift stops the operation for review.

`metadata --reuse-sources` reparses an already captured set; it is not a new/current HTTP observation.
If catalog or cache inputs change, acquire fresh missing-model references rather than pretend old artifacts are current.

## Verification

```bash
AI_SUITE_ROOT="$AI_SUITE" PYTHONDONTWRITEBYTECODE=1 python3 test-sync-nvidia-nim-models.py
ruff check sync-nvidia-nim-models.py test-sync-nvidia-nim-models.py
ruff format --check sync-nvidia-nim-models.py test-sync-nvidia-nim-models.py
```

Tests cover cached-ID immunity, user overrides, missing limits, duplicate/empty inputs, managed cache convergence,
drift refusal, non-NVIDIA bytes/comments, CRLF, idempotency, and absence of fabricated prices/free names.
No inference or model-generation request is part of the sync workflow.
