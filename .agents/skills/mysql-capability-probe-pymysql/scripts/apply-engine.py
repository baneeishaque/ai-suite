#!/usr/bin/env python3
"""Idempotently switch one or more tables to a target storage engine via
`ALTER TABLE … ENGINE=<target>`. Skips tables already on the target engine.

Use cases:
- Migrating legacy MyISAM tables to InnoDB as a prerequisite for FOREIGN KEY
  constraints (MyISAM silently drops FK clauses).
- Migrating tables to Aria on MariaDB for crash-safe MyISAM-like behavior.

Usage:
    apply-engine.py --secrets <path> --engine InnoDB --table t1 [--table t2 ...]

Cost note: ALTER TABLE ENGINE=<x> rebuilds the entire table (ALGORITHM=COPY for
MyISAM->InnoDB). Disk free space ~= table size required during the copy.
Lock semantics: blocks writes for the duration; sub-second for small tables,
minutes-to-hours for multi-GB tables. Use probe-server-flavor.py --table <t>
beforehand to budget the window.

Verdict lines (one per table):
    SKIP: <table> already on <engine>
    EXEC: ALTER TABLE <table> ENGINE=<engine>  (<seconds>s)
    OK:   <table> now on <engine>
    FAIL: <table> -- <error>

Exit codes:
    0  all tables on target engine after the run
    1  one or more tables FAILed
    2  bad arguments / unreadable secrets
"""
import argparse
import sys
import time


def parse_secrets(path):
    out = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, _, v = line.partition('=')
                out[k.strip()] = v.strip()
    except OSError as e:
        print(f"PROBE_CONFIG_ERROR: cannot read secrets: {e}", file=sys.stderr)
        sys.exit(2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--secrets', required=True)
    ap.add_argument('--engine', required=True,
                    help='Target storage engine (e.g. InnoDB, Aria, MyISAM).')
    ap.add_argument('--table', required=True, action='append',
                    help='Table name; may be repeated.')
    args = ap.parse_args()

    try:
        import pymysql
    except ImportError:
        print("PROBE_CONFIG_ERROR: pymysql not installed", file=sys.stderr)
        sys.exit(2)

    s = parse_secrets(args.secrets)
    for k in ('DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME'):
        if k not in s:
            print(f"PROBE_CONFIG_ERROR: missing {k} in secrets", file=sys.stderr)
            sys.exit(2)

    try:
        c = pymysql.connect(host=s['DB_HOST'], port=int(s.get('DB_PORT', '3306')),
                            user=s['DB_USER'], password=s['DB_PASSWORD'],
                            database=s['DB_NAME'])
    except Exception as e:
        print(f"PROBE_CONNECT_ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    db = s['DB_NAME']
    target = args.engine
    failed = False

    with c.cursor() as cur:
        for table in args.table:
            cur.execute("""SELECT ENGINE FROM information_schema.TABLES
                           WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s""", (db, table))
            row = cur.fetchone()
            if not row:
                print(f"FAIL: {table} -- table not found in schema {db}")
                failed = True
                continue
            current = row[0]
            if current.lower() == target.lower():
                print(f"SKIP: {table} already on {current}")
                continue
            try:
                t0 = time.time()
                # Engine name is operator-supplied, not user input; quote table only.
                cur.execute(f"ALTER TABLE `{table}` ENGINE={target}")
                dt = time.time() - t0
                print(f"EXEC: ALTER TABLE {table} ENGINE={target}  ({dt:.2f}s)")
            except Exception as e:
                print(f"FAIL: {table} -- {e}")
                failed = True
                continue
            cur.execute("""SELECT ENGINE FROM information_schema.TABLES
                           WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s""", (db, table))
            new = cur.fetchone()[0]
            if new.lower() == target.lower():
                print(f"OK:   {table} now on {new}")
            else:
                print(f"FAIL: {table} -- still on {new} after ALTER")
                failed = True
    c.commit()
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
