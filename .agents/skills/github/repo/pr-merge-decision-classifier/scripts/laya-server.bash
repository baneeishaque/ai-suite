#!/usr/bin/env bash
# laya-server.bash — manage a local `laya-system-one` server (start | stop | restart | status | health).
#
# The server speaks the TypeSafe Jev /v1/systemone protocol on 127.0.0.1 and is
# keyless unless the package supports a key flag (kept out of this wrapper by
# default). Logs and the PID file live in ${TMPDIR:-/tmp} so the script stays
# portable and never writes inside the repository.
#
# Language tier: Tier-2 borderline (Bash, POSIX process glue), documented per
# skill-factory §2.2.1.1 #2. Rationale per ai-agent-rules/scripting-language-
# selection-rules.md §3.2 (OS orchestration is shell-glue territory), §3.3
# (pwsh is a non-default install on the macOS/Linux hosts this skill targets)
# and §2.4 (call-native-binaries sequences are not Python's sweet spot). The
# body is >=80% process glue (nohup launch, PID file, kill -0 liveness, lsof
# port check, curl health poll), so bash is the native, always-present shell.
# Extension is .bash per the same mandate (never .sh).
#
# Exit codes: 0 = success/healthy, 1 = not running, 2 = usage/startup failure.

set -euo pipefail

PKG="laya-system-one@1.0.0"
PORT=8081
HOST=127.0.0.1
WAIT_SECS=600
CMD=""

usage() {
    cat <<'EOF'
Usage: laya-server.bash <start|stop|restart|status|health> [--port N] [--host H] [--wait SECS]

  start    Start the server in the background and wait for /health (default port 8081)
  stop     Stop the server recorded in the PID file
  restart  Stop (tolerating "not running") then start
  status   Print health JSON when running; exit 1 when not
  health   Alias of status
EOF
}

if [ $# -eq 0 ]; then
    usage >&2
    exit 2
fi
CMD="$1"
shift

while [ $# -gt 0 ]; do
    case "$1" in
        --port)
            PORT="${2:?--port needs a value}"
            shift 2
            ;;
        --host)
            HOST="${2:?--host needs a value}"
            shift 2
            ;;
        --wait)
            WAIT_SECS="${2:?--wait needs a value}"
            shift 2
            ;;
        *)
            echo "ERROR: unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

LOG="${TMPDIR:-/tmp}/laya-system-one.${PORT}.log"
PIDFILE="${TMPDIR:-/tmp}/laya-system-one.${PORT}.pid"
HEALTH_URL="http://${HOST}:${PORT}/health"

health() {
    curl -s --max-time 3 "$HEALTH_URL"
}

is_healthy() {
    health >/dev/null 2>&1
}

wait_for_health() {
    local waited=0
    while [ "$waited" -lt "$WAIT_SECS" ]; do
        if is_healthy; then
            echo "laya-system-one healthy on ${HOST}:${PORT} after ~${waited}s"
            health
            echo
            return 0
        fi
        sleep 5
        waited=$((waited + 5))
    done
    echo "ERROR: laya-system-one did not become healthy within ${WAIT_SECS}s; see ${LOG}" >&2
    return 2
}

start() {
    if is_healthy; then
        echo "laya-system-one already running on ${HOST}:${PORT}"
        return 0
    fi
    if lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
        echo "ERROR: port ${PORT} is already in use by another process" >&2
        return 2
    fi
    echo "starting laya-system-one on ${HOST}:${PORT} (log: ${LOG})"
    nohup npx --yes "$PKG" --port "$PORT" --host "$HOST" >"$LOG" 2>&1 &
    echo $! >"$PIDFILE"
    wait_for_health
}

stop() {
    if [ ! -f "$PIDFILE" ]; then
        if is_healthy; then
            echo "ERROR: server is healthy but no PID file at ${PIDFILE}; stop it manually" >&2
            return 2
        fi
        echo "laya-system-one not running"
        return 0
    fi
    local pid
    pid="$(cat "$PIDFILE")"
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null || true
        for _ in $(seq 1 20); do
            kill -0 "$pid" 2>/dev/null || break
            sleep 1
        done
        if kill -0 "$pid" 2>/dev/null; then
            echo "ERROR: process ${pid} did not stop" >&2
            return 2
        fi
    fi
    rm -f "$PIDFILE"
    echo "laya-system-one stopped (pid ${pid})"
}

status() {
    if is_healthy; then
        health
        echo
        return 0
    fi
    echo "laya-system-one not running on ${HOST}:${PORT}"
    return 1
}

case "$CMD" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop || true
        start
        ;;
    status | health)
        status
        ;;
    *)
        echo "ERROR: unknown command: $CMD" >&2
        usage >&2
        exit 2
        ;;
esac
