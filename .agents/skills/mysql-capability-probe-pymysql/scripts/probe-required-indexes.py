#!/usr/bin/env python3
"""
probe-required-indexes.py — Verify that one or more (table, column) pairs each
have an index whose first key part (`SEQ_IN_INDEX=1`) is that column.

This is the prerequisite check for any query that relies on single-column index
seeks — e.g., delete-gate EXISTS subqueries (see
`remote-mysql-roundtrip-minimization` §5.4).

Inputs:
    --secrets <path>       KEY=VALUE secrets file (DB_HOST, DB_USER, DB_PASSWORD,
                           DB_NAME, optional DB_PORT). Format identical to
                           probe-multi-statement.py.
    --check <table>.<col>  Repeatable. Each occurrence adds one required pair.

Output (stdout): one line per pair:
    INDEX_PRESENT: <table>.<col>  <index_name> (UNIQUE|non-unique)
    INDEX_MISSING: <table>.<col>
followed by:
    --- SUMMARY: <present>/<total> present, <missing> missing ---

Exit code:
    0  all required indexes present
    1  at least one missing
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


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument('--secrets', required=True)
    ap.add_argument(
        '--check', action='append', required=True, metavar='TABLE.COLUMN',
        help='Required: table.column pair to verify. Repeat for multiple pairs.',
    )
    args = ap.parse_args()

    pairs = []
    for raw in args.check:
        if '.' not in raw:
            print(f"PROBE_CONFIG_ERROR: --check must be TABLE.COLUMN: {raw!r}",
                  file=sys.stderr)
            sys.exit(2)
        t, _, c = raw.partition('.')
        pairs.append((t.strip(), c.strip()))

    try:
        import pymysql  # type: ignore
    except ImportError:
        print("PROBE_CONFIG_ERROR: pymysql not installed", file=sys.stderr)
        sys.exit(2)

    try:
        s = parse_secrets(args.secrets)
    except OSError as e:
        print(f"PROBE_CONFIG_ERROR: cannot read secrets: {e}", file=sys.stderr)
        sys.exit(2)

    for k in ('DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME'):
        if k not in s:
            print(f"PROBE_CONFIG_ERROR: missing {k} in secrets", file=sys.stderr)
            sys.exit(2)

    conn = pymysql.connect(
        host=s['DB_HOST'], port=int(s.get('DB_PORT', '3306')),
        user=s['DB_USER'], password=s['DB_PASSWORD'],
        database=s['DB_NAME'],
    )
    missing = 0
    try:
        with conn.cursor() as cur:
            for table, col in pairs:
                cur.execute(
                    "SELECT INDEX_NAME, NON_UNIQUE "
                    "FROM information_schema.STATISTICS "
                    "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s "
                    "  AND COLUMN_NAME=%s AND SEQ_IN_INDEX=1 "
                    "ORDER BY NON_UNIQUE, INDEX_NAME LIMIT 1",
                    (s['DB_NAME'], table, col),
                )
                row = cur.fetchone()
                if row:
                    idx, non_unique = row
                    uniq = "UNIQUE" if non_unique == 0 else "non-unique"
                    print(f"INDEX_PRESENT: {table}.{col}  {idx} ({uniq})")
                else:
                    print(f"INDEX_MISSING: {table}.{col}")
                    missing += 1
    finally:
        conn.close()

    print(f"--- SUMMARY: {len(pairs) - missing}/{len(pairs)} present, "
          f"{missing} missing ---")
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()
