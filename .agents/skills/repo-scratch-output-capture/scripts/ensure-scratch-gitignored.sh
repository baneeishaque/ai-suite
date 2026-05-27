#!/usr/bin/env bash
# ensure-scratch-gitignored.sh
# Idempotently create <repo-root>/scratch/ and add "scratch/" to .gitignore.
# Emits the absolute path to scratch/ on stdout (suitable for command substitution).
# Usage: SCRATCH="$(bash path/to/ensure-scratch-gitignored.sh)"

set -euo pipefail

REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "[ensure-scratch-gitignored] ERROR: not inside a git repository" >&2
    exit 1
}

SCRATCH="$REPO/scratch"
GITIGNORE="$REPO/.gitignore"

mkdir -p "$SCRATCH"

if [ -f "$GITIGNORE" ]; then
    grep -qxF 'scratch/' "$GITIGNORE" 2>/dev/null || echo 'scratch/' >> "$GITIGNORE"
else
    echo 'scratch/' > "$GITIGNORE"
fi

echo "$SCRATCH"
