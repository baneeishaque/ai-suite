#!/bin/bash
# Register git aliases with pre-flight check chaining.
# Idempotent: safe to run on every checkout.
#
# Usage: bash scripts/register-alias.bash
#
# Tier: 2 (Bash) — shell glue.
# See scripting-language-selection-rules.md section 3.4.

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$REPO_ROOT" ]; then
  echo "Error: not in a git repository"
  exit 1
fi

LIB_SCRIPT="$REPO_ROOT/scripts/githooks/lib.bash"
if [ ! -f "$LIB_SCRIPT" ]; then
  echo "Warning: $LIB_SCRIPT not found — skipping alias registration"
  echo "Run git-repo-hook-chain's setup-repo-hooks.bash first."
  exit 0
fi

git config alias.status "!bash $LIB_SCRIPT status"
echo "[alias-preflight] Registered: git status -> preflight check + real status"
