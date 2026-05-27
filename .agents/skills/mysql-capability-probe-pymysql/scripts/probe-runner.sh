#!/usr/bin/env bash
# probe-runner.sh — Orchestrates a PyMySQL probe end-to-end:
#   1. Resolves mise global python via DIRECT install path (no `mise exec`
#      cascade — see mise-tool-management Layer 5).
#   2. Idempotently installs pymysql into that python (--user).
#   3. Ensures <repo-root>/scratch/ exists and is gitignored
#      (see repo-scratch-output-capture).
#   4. Runs the named probe script with --secrets <path>, redirecting
#      stdout/stderr to scratch/<probe-name>.out|err.
#
# Usage:
#   probe-runner.sh --probe <probe-script.py> --secrets <act.secrets-path> [--name <slug>]
#
# Defaults:
#   --name = basename of probe script minus .py
#
# Exit code: forwards the probe's exit code (0 supported, 1 not, 2 config).

set -euo pipefail

PROBE=""
SECRETS=""
NAME=""

while [ $# -gt 0 ]; do
    case "$1" in
        --probe)   PROBE="$2"; shift 2 ;;
        --secrets) SECRETS="$2"; shift 2 ;;
        --name)    NAME="$2"; shift 2 ;;
        -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
        *) echo "[probe-runner] unknown arg: $1" >&2; exit 2 ;;
    esac
done

[ -n "$PROBE" ]   || { echo "[probe-runner] --probe required" >&2; exit 2; }
[ -n "$SECRETS" ] || { echo "[probe-runner] --secrets required" >&2; exit 2; }
[ -f "$PROBE" ]   || { echo "[probe-runner] probe script not found: $PROBE" >&2; exit 2; }
[ -f "$SECRETS" ] || { echo "[probe-runner] secrets file not found: $SECRETS" >&2; exit 2; }

[ -n "$NAME" ] || NAME="$(basename "$PROBE" .py)"

# 1. Resolve mise global python (direct path; bypass `mise exec` cascade).
MISE_PY_ROOT="$HOME/.local/share/mise/installs/python"
if [ ! -d "$MISE_PY_ROOT" ]; then
    echo "[probe-runner] ERROR: no mise python installs at $MISE_PY_ROOT" >&2
    echo "[probe-runner] See mise-tool-management Layer 3 (Mise Python Setup)." >&2
    exit 2
fi
PY_VER="$(ls "$MISE_PY_ROOT" | sort -V | tail -1)"
PY_BIN="$MISE_PY_ROOT/$PY_VER/bin/python"
PIP_BIN="$MISE_PY_ROOT/$PY_VER/bin/pip"
[ -x "$PY_BIN" ] || { echo "[probe-runner] no python binary at $PY_BIN" >&2; exit 2; }

# 2. Ensure pymysql is installed (idempotent — pip exits 0 if up-to-date).
if ! "$PY_BIN" -c "import pymysql" 2>/dev/null; then
    SCRATCH_REPO="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
    mkdir -p "$SCRATCH_REPO/scratch"
    "$PIP_BIN" install --user --quiet pymysql \
        > "$SCRATCH_REPO/scratch/pip-pymysql.out" \
        2> "$SCRATCH_REPO/scratch/pip-pymysql.err" \
        || { echo "[probe-runner] pip install pymysql failed; see scratch/pip-pymysql.err" >&2; exit 2; }
fi

# 3. Ensure scratch dir + gitignore.
SCRATCH_HELPER="$(cd "$(dirname "$0")/../../repo-scratch-output-capture/scripts" \
    && pwd)/ensure-scratch-gitignored.sh"
if [ -x "$SCRATCH_HELPER" ]; then
    SCRATCH="$(bash "$SCRATCH_HELPER")"
else
    SCRATCH="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/scratch"
    mkdir -p "$SCRATCH"
fi

# 4. Run the probe with captured streams.
set +e
"$PY_BIN" "$PROBE" --secrets "$SECRETS" \
    > "$SCRATCH/$NAME.out" \
    2> "$SCRATCH/$NAME.err"
RC=$?
set -e

echo "[probe-runner] exit=$RC  see $SCRATCH/$NAME.{out,err}"
echo "--- verdict ---"
cat "$SCRATCH/$NAME.out" || true
exit $RC
