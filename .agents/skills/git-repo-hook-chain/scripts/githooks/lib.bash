#!/bin/bash
# Single entry point for all repo hooks + alias preflight.
# Invoked by: pre-commit, pre-push, pre-merge-commit, pre-rebase wrappers
#             and by git status alias.
#
# Usage: lib.bash <caller-name>
#   caller-name is typically "$0" from hook wrapper or "status" from alias.
#
# Dispatches:
#   pre-commit | pre-push | pre-merge-commit | pre-rebase
#       -> run check, block if fails
#   status
#       -> run check (output visible), then exec real git status
#   * (unknown)
#       -> exit 0 (allow)
#
# Environment:
#   GATE_CHECK_SCRIPT  path to the check script (set by domain composer)
#
# Tier: 2 (Bash) — shell glue; must work in git hook context.
# See scripting-language-selection-rules.md section 3.4.

set -euo pipefail

CALLER=$(basename "${1:-unknown}")
GATE_CHECK_SCRIPT="${GATE_CHECK_SCRIPT:-}"

run_check() {
  if [ -n "$GATE_CHECK_SCRIPT" ] && [ -x "$GATE_CHECK_SCRIPT" ]; then
    bash "$GATE_CHECK_SCRIPT"
    return $?
  fi
  return 0
}

case "$CALLER" in
  pre-commit|pre-push|pre-merge-commit|pre-rebase)
    run_check
    rc=$?
    if [ $rc -ne 0 ]; then
      echo "[gate] BLOCKED: meaningful change detected ($CALLER)"
      echo "[gate] Use --no-verify (commit) or SKIP_GATE=1 (push) to bypass"
      exit $rc
    fi
    exit 0
    ;;
  status)
    echo ""
    echo "--- [gate preflight check] ---"
    run_check
    rc=$?
    echo "--- gate exit: $rc ---"
    echo ""
    exec git status
    ;;
  *)
    exit 0
    ;;
esac
