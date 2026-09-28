#!/bin/bash
# run-swh-verify.bash — Run SWH ingest verification with CI-friendly status.
#
# Required env: AI_SUITE_HEAD, AI_AGENT_RULES_HEAD,
#   AI_SUITE_ORIGIN, AI_AGENT_RULES_ORIGIN, VERIFY_SCRIPT
# Optional env: TRIGGER_SAVE ("true" to fire best-effort Save-code-now POSTs).
#
# Exit mapping: VERIFIED(0)->pass; PENDING(1)->::warning:: + pass (ingest
# lag is not breakage); FAILED(2)->::error:: + fail.

set -euo pipefail

for var in AI_SUITE_HEAD AI_AGENT_RULES_HEAD AI_SUITE_ORIGIN \
  AI_AGENT_RULES_ORIGIN VERIFY_SCRIPT; do
  if [[ -z "${!var:-}" ]]; then
    echo "::error::Required env var $var is not set."
    exit 1
  fi
done

ARGS=(
  --check "$AI_SUITE_ORIGIN,$AI_SUITE_HEAD"
  --check "$AI_AGENT_RULES_ORIGIN,$AI_AGENT_RULES_HEAD"
)
if [[ "${TRIGGER_SAVE:-false}" == "true" ]]; then
  ARGS+=(--trigger-save)
fi

set +e
python3 "$VERIFY_SCRIPT" "${ARGS[@]}"
STATUS=$?
set -e

if [[ $STATUS -eq 0 ]]; then
  echo "SWH ingest verified for both origins."
elif [[ $STATUS -eq 1 ]]; then
  echo "::warning::SWH ingest pending — HEAD not yet in latest snapshot (crawler lag). Rechecks next push."
else
  echo "::error::SWH verification failed (origin unknown or API error). Run swh-save-code-now locally, then re-run."
  exit 1
fi