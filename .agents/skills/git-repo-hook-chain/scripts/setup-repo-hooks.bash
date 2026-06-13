#!/bin/bash
# Bootstrap repo-level hooks for this repository.
# Idempotent: safe to run on every checkout.
#
# Usage: bash scripts/setup-repo-hooks.bash
#
# Tier: 2 (Bash) — shell glue.
# See scripting-language-selection-rules.md section 3.4.

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$REPO_ROOT" ]; then
  echo "Error: not in a git repository"
  exit 1
fi

HOOKS_DIR="$REPO_ROOT/scripts/githooks"
if [ ! -d "$HOOKS_DIR" ]; then
  echo "Warning: $HOOKS_DIR does not exist — no hooks to activate"
  echo "Create this directory and populate with hooks to enable the hook chain."
  exit 0
fi

git config core.hooksPath scripts/githooks
echo "[repo-hooks] Set core.hooksPath = scripts/githooks"

echo "[repo-hooks] Repo hooks active: pre-commit, pre-push, pre-merge-commit, pre-rebase"
