#!/bin/bash
# Check claude config files for meaningful vs trivial changes.
# Exit 0 = only trivial timestamp changes (allow git operation)
# Exit 1 = meaningful change detected (block git operation)
#
# Tier: 2 (Bash) — shell glue; discovers files and shells out to
# Python base script for JSON comparison.
# See scripting-language-selection-rules.md section 3.4.

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)

# Resolve the base JSON comparator script.
# Priority: env var > anchored relative to this script's location > error
JSON_COMPARE="${JSON_COMPARE_SCRIPT:-}"
if [ -z "$JSON_COMPARE" ]; then
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  JSON_COMPARE="$SCRIPT_DIR/../../json-content-compare-ignore-keys/scripts/json-content-compare-ignore-keys.py"
fi

BLOCKED=0

# ---------------------------------------------------------------------------
# Check A — claude/.last-cleanup
#   Must contain only a valid ISO 8601 timestamp.
# ---------------------------------------------------------------------------
CLEANUP_FILE="$REPO_ROOT/claude/.last-cleanup"
if [ -f "$CLEANUP_FILE" ]; then
  CONTENT=$(cat "$CLEANUP_FILE" 2>/dev/null || true)
  if echo "$CONTENT" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}'; then
    :  # Content is an ISO timestamp — trivial change, pass.
  else
    echo "[claude-gate] BLOCKED: $CLEANUP_FILE contains non-timestamp content"
    BLOCKED=1
  fi
fi

# ---------------------------------------------------------------------------
# Check B — claude/plugins/known_marketplaces.json
#   Compare structural content, ignoring the 'lastUpdated' key.
# ---------------------------------------------------------------------------
MARKETPLACES_FILE="$REPO_ROOT/claude/plugins/known_marketplaces.json"
if [ -f "$MARKETPLACES_FILE" ]; then
  if [ -x "$JSON_COMPARE" ]; then
    python3 "$JSON_COMPARE" --file "$MARKETPLACES_FILE" --ignore-keys lastUpdated \
      || BLOCKED=1
  else
    echo "[claude-gate] WARNING: JSON compare script not found at:"
    echo "[claude-gate]   $JSON_COMPARE"
    echo "[claude-gate] Install json-content-compare-ignore-keys skill or"
    echo "[claude-gate] set JSON_COMPARE_SCRIPT env var."
    BLOCKED=1
  fi
fi

exit $BLOCKED
