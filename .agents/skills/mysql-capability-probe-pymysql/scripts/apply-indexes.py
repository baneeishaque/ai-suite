#!/usr/bin/env python3
"""
apply-indexes.py — Idempotently add single-column indexes via `ALTER TABLE …
ADD INDEX`. Skips any (table, column) whose first-key-part index already exists
according to `information_schema.STATISTICS`.

This is the writer-side counterpart to `probe-required-indexes.py`: probe first,
add what's missing.

Inputs:
    --secrets <path>
    --index <table>.<col>[:<index_name>]      (repeatable)

If <index_name> is omitted, defaults to `idx_<col>`.

Output (stdout):
    SKIP: <table>.<col> already indexed (<existing>)
    EXEC: ALTER TABLE `<table>` ADD INDEX `<idx>` (`<col>`)
    OK:   created <idx> on <table>.<col>
    FAIL: <idx> -> <ExceptionClass>: <message>

Exit code:
    0  every requested index now exists (added or already present)
    1  at least one ALTER failed
    2  configuration / connection error
"""
import argparse
import sys


def parse_secrets(path):
    out = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, _, v = line.partition('=')
            out[k.strip()] = v.strip()
    return out


def parse_spec(raw):
    """table.col[:idx_name] -> (table, col, idx_name)"""
    if '.' not in raw:
        raise ValueError(f"--index must be TABLE.COL[:IDX_NAME]: {raw!r}")
    head, _, idx = raw.partition(':')
    t, _, c = head.partition('.')
    t = t.strip(); c = c.strip(); idx = idx.strip() or f"idx_{c}"
    if not t or not c:
        raise ValueError(f"--index empty side: {raw!r}")
    return t, c, idx


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument('--secrets', required=True)
    ap.add_argument(
        '--index', action='append', required=True,
        metavar='TABLE.COL[:IDX_NAME]',
        help='Repeatable. One single-column index to ensure.',
    )
    args = ap.parse_args()

    try:
        specs = [parse_spec(x) for x in args.index]
    except ValueError as e:
        print(f"PROBE_CONFIG_ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        import pymysql  # type: ignore
    except ImportError:
        print("PROBE_CONFIG_ERROR: pymysql not installed", file=sys.stderr)
        sys.exit(2)

    s = parse_secrets(args.secrets)
    for k in ('DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME'):
        if k not in s:
            print(f"PROBE_CONFIG_ERROR: missing {k}", file=sys.stderr)
            sys.exit(2)

    rc = 0
    conn = pymysql.connect(
        host=s['DB_HOST'], port=int(s.get('DB_PORT', '3306')),
        user=s['DB_USER'], password=s['DB_PASSWORD'],
        database=s['DB_NAME'], autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            for table, col, idx in specs:
                cur.execute(
                    "SELECT INDEX_NAME FROM information_schema.STATISTICS "
                    "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s "
                    "  AND COLUMN_NAME=%s AND SEQ_IN_INDEX=1 LIMIT 1",
                    (s['DB_NAME'], table, col),
                )
                row = cur.fetchone()
                if row:
                    print(f"SKIP: {table}.{col} already indexed ({row[0]})")
                    continue
                ddl = f"ALTER TABLE `{table}` ADD INDEX `{idx}` (`{col}`)"
                print(f"EXEC: {ddl}")
                try:
                    cur.execute(ddl)
                    print(f"OK:   created {idx} on {table}.{col}")
                except Exception as e:
                    print(f"FAIL: {idx} -> {type(e).__name__}: {e}")
                    rc = 1
    finally:
        conn.close()
    sys.exit(rc)


if __name__ == '__main__':
    main()
