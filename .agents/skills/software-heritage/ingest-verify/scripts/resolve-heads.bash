#!/bin/bash
# resolve-heads.bash — Resolve expected SHAs for SWH verification.
#
# Usage: bash resolve-heads.bash <submodule-path>
# Writes AI_SUITE_HEAD and AI_AGENT_RULES_HEAD to $GITHUB_OUTPUT.
# The submodule SHA comes from the superproject gitlink (no submodule
# checkout needed), so actions/checkout with submodules:false suffices.

set -euo pipefail

SUBMODULE_PATH="${1:?error: submodule path argument is required}"

if [[ -z "${GITHUB_OUTPUT:-}" ]]; then
  echo "::error::GITHUB_OUTPUT is not set (run inside GitHub Actions)."
  exit 1
fi

AI_SUITE_HEAD="$(git rev-parse HEAD)"
if [[ ! "$AI_SUITE_HEAD" =~ ^[0-9a-f]{40}$ ]]; then
  echo "::error::Could not resolve superproject HEAD."
  exit 1
fi

SUBMODULE_LINE="$(git submodule status -- "$SUBMODULE_PATH" || true)"
AI_AGENT_RULES_HEAD="$(echo "$SUBMODULE_LINE" | awk '{print $1}' | sed 's/^[-+U]//')"
if [[ ! "$AI_AGENT_RULES_HEAD" =~ ^[0-9a-f]{40}$ ]]; then
  echo "::error::Could not resolve gitlink SHA for submodule '$SUBMODULE_PATH'."
  exit 1
fi

{
  echo "AI_SUITE_HEAD=$AI_SUITE_HEAD"
  echo "AI_AGENT_RULES_HEAD=$AI_AGENT_RULES_HEAD"
} >> "$GITHUB_OUTPUT"

echo "Resolved AI_SUITE_HEAD=$AI_SUITE_HEAD"
echo "Resolved AI_AGENT_RULES_HEAD=$AI_AGENT_RULES_HEAD"