#!/usr/bin/env bash
# Defines the extraction pipeline executed remotely via SSH standard input (bash -s)
# Requires Bash 3.2+

REMOTE_ENV_PATH="$1"
DUMP_FORMAT_FLAG="$2"
ENV_DB_KEY="$3"
DUMP_TOOL="${4:-pg_dump}"

# 0. Core Requirements Enforcement
if (( BASH_VERSINFO[0] < 3 || (BASH_VERSINFO[0] == 3 && BASH_VERSINFO[1] < 2) )); then
    echo "ERR:bash_version_unsupported: Requires 3.2+" >&2
    exit 1
fi

# Validate dump tool selection
if [ "$DUMP_TOOL" != "pg_dump" ] && [ "$DUMP_TOOL" != "pg_dumpall" ] && [ "$DUMP_TOOL" != "pg_dumpall_split" ]; then
    echo "ERR:invalid_dump_tool_$DUMP_TOOL" >&2
    exit 1
fi

# 1. Remote Toolchain Preflight
# pg_dumpall_split needs pg_dumpall + pg_dump + psql; others need only their own binary.
if [ "$DUMP_TOOL" = "pg_dumpall_split" ]; then
    for cmd in grep cut sed pg_dumpall pg_dump psql; do
        command -v "$cmd" >/dev/null || { echo "ERR:missing_dependency_$cmd" >&2; exit 1; }
    done
else
    for cmd in grep cut sed "$DUMP_TOOL"; do
        command -v "$cmd" >/dev/null || { echo "ERR:missing_dependency_$cmd" >&2; exit 1; }
    done
fi

[ -f "$REMOTE_ENV_PATH" ] || { echo "ERR:env_not_found" >&2; exit 1; }

# 2. Credential Extraction
MATCH_COUNT=$(grep --count "^${ENV_DB_KEY}=" "$REMOTE_ENV_PATH")
if [ "$MATCH_COUNT" -eq 0 ]; then
    echo "ERR:${ENV_DB_KEY}_not_found" >&2
    exit 1
elif [ "$MATCH_COUNT" -gt 1 ]; then
    echo "ERR:${ENV_DB_KEY}_multiple_entries_found" >&2
    exit 1
fi

# Extract strictly single known key and strip quotes/whitespace
DB_URL=$(grep "^${ENV_DB_KEY}=" "$REMOTE_ENV_PATH" | cut --delimiter="=" --fields=2- | sed --expression='s/^[[:space:]]*//' --expression='s/[[:space:]]*$//' --expression='s/^["'\'']//' --expression='s/["'\'']$//')

if [ -z "$DB_URL" ]; then
    echo "ERR:database_url_empty" >&2
    exit 1
fi

if [[ ! "$DB_URL" =~ ^postgres(ql)?://[^[:space:]]+$ ]]; then
    echo "ERR:invalid_postgres_url_format" >&2
    exit 1
fi

# 2.5 Industrial URI Normalization (Resolving unencoded @ symbols in passwords)
# If a db password contains an '@' natively (e.g., in a lax .env file), pg_dump fractures hostname parsing.
if [[ "$DB_URL" =~ ^(postgres(ql)?://[^:]+:)(.*)(@[^@/]+(:[0-9]+)?/.*)$ ]]; then
    PREFIX="${BASH_REMATCH[1]}"
    PASS="${BASH_REMATCH[3]}"
    SUFFIX="${BASH_REMATCH[4]}"
    # URL encode all '@' symbols strictly within the isolated password boundary
    PASS="${PASS//@/%40}"
    DB_URL="${PREFIX}${PASS}${SUFFIX}"
fi

# 3. Streaming Execution
# Note: pg_dump / pg_dumpall use stdout for the dump file by default when -f is not provided.
if [ "$DUMP_TOOL" = "pg_dumpall" ]; then
    # Full cluster logical backup: every database, roles, tablespaces, DB-level
    # settings (encoding, collation, connection limits), privileges, extensions.
    # pg_dumpall emits plain SQL only — DUMP_FORMAT_FLAG is intentionally ignored.
    pg_dumpall --dbname="$DB_URL" --no-password

elif [ "$DUMP_TOOL" = "pg_dumpall_split" ]; then
    # ClusterSplit: globals as plain SQL + each database as a custom (compressed) archive.
    # Emits a length-prefixed multiplexed byte stream:
    #   FILE:<name>:<20-digit-zero-padded-size>:\n<bytes>  (repeated per file)
    #   DONE\n
    # The receiver splits the stream into individual files without any remote temp storage
    # beyond one dump at a time (bounded by the largest single database).

    # Emit one file into the multiplexed stream.
    # Usage: emit_stream_file <output-filename> <command> [args...]
    emit_stream_file() {
        local label="$1"; shift
        local tmpfile tmperr
        tmpfile=$(mktemp) || { printf 'ERR:mktemp_failed:%s\n' "$label" >&2; exit 1; }
        tmperr=$(mktemp)  || { rm -f "$tmpfile"; printf 'ERR:mktemp_failed:%s\n' "$label" >&2; exit 1; }
        if ! "$@" > "$tmpfile" 2> "$tmperr"; then
            local errmsg
            errmsg=$(tr '\n' ' ' < "$tmperr" | sed 's/[[:space:]]*$//')
            rm -f "$tmpfile" "$tmperr"
            printf 'ERR:dump_failed:%s:%s\n' "$label" "$errmsg" >&2
            exit 1
        fi
        rm -f "$tmperr"
        local size
        size=$(wc -c < "$tmpfile" | tr -d '[:space:]')
        # Header line: FILE:<name>:<020d size>:\n  — fixed-width size allows O(1) parsing
        printf 'FILE:%s:%020d:\n' "$label" "$size"
        cat "$tmpfile"
        rm -f "$tmpfile"
    }

    # Build a per-database connection URL by swapping the database name segment.
    # Handles:  postgres://user:pass@host:port/dbname
    #           postgres://user:pass@host:port/dbname?sslmode=require
    make_db_url() {
        local dbname="$1"
        local prefix="${DB_URL%/*}/"         # everything up to and including the last '/'
        local after_slash="${DB_URL##*/}"    # dbname  or  dbname?params
        local suffix=""
        if [[ "$after_slash" == *"?"* ]]; then
            suffix="?${after_slash#*?}"
        fi
        printf '%s%s%s' "$prefix" "$dbname" "$suffix"
    }

    # 3a. Globals: roles (without password hashes — non-superuser can't read pg_authid),
    # tablespaces, database-level settings, privileges.
    # --no-role-passwords: role hashes excluded; reset passwords on staging post-restore.
    emit_stream_file "globals.sql" \
        pg_dumpall --dbname="$DB_URL" --globals-only --no-role-passwords --no-password

    # 3b. Enumerate every non-template connectable database
    DATABASES=$(psql "$DB_URL" --no-password -Atc \
        "SELECT datname FROM pg_database WHERE NOT datistemplate AND datallowconn ORDER BY datname" 2>/dev/null)
    if [ -z "$DATABASES" ]; then
        printf 'ERR:no_connectable_databases_found\n' >&2
        exit 1
    fi

    # 3c. One custom-format archive per database (already zlib-compressed internally)
    while IFS= read -r dbname; do
        [ -z "$dbname" ] && continue
        emit_stream_file "${dbname}.dump" \
            pg_dump --dbname="$(make_db_url "$dbname")" --format=custom --no-password
    done <<< "$DATABASES"

    printf 'DONE\n'

else
    pg_dump --dbname="$DB_URL" $DUMP_FORMAT_FLAG --no-password
fi
