#!/usr/bin/env python3
"""Probe server flavor, version, default storage engine, and per-engine
transaction / FK / savepoint support.

Distinguishes MySQL from MariaDB (wire-compatible but with diverging
system variables — e.g. MySQL exposes @@innodb_version, MariaDB does
not). Use BEFORE writing any DDL or referring to engine-specific docs.

Usage:
    probe-server-flavor.py --secrets <path-to-secrets.env>

Secrets file (KEY=VALUE, lines starting with # ignored):
    DB_HOST=...
    DB_PORT=3306
    DB_USER=...
    DB_PASSWORD=...
    DB_NAME=...

Optional:
    --table <name>    Also print row count + data/index size for one table.

Verdict line:
    SERVER_FLAVOR: <MySQL|MariaDB|Unknown>  VERSION: <version>  DEFAULT_ENGINE: <engine>

Exit codes:
    0  probe ran cleanly
    1  connection or query failed
    2  bad arguments / unreadable secrets
"""
import argparse
import sys


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
    ap.add_argument('--table', default=None,
                    help='Optional table name; print TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH.')
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
        sys.exit(1)

    db = s['DB_NAME']
    with c.cursor() as cur:
        cur.execute("SELECT VERSION()")
        version = cur.fetchone()[0]
        cur.execute("SELECT @@version_comment")
        comment = cur.fetchone()[0]

        flavor = 'Unknown'
        v_low = version.lower()
        c_low = (comment or '').lower()
        if 'mariadb' in v_low or 'mariadb' in c_low:
            flavor = 'MariaDB'
        elif 'mysql' in c_low or version[0:1].isdigit():
            flavor = 'MySQL'

        print(f"=== server ===")
        print(f"  VERSION  : {version}")
        print(f"  COMMENT  : {comment}")

        cur.execute("SELECT @@default_storage_engine")
        default_engine = cur.fetchone()[0]
        print(f"  DEFAULT  : {default_engine}")

        cur.execute("SHOW ENGINES")
        print("\n=== engines (SUPPORT=YES or DEFAULT) ===")
        for row in cur.fetchall():
            if row[1] in ('YES', 'DEFAULT'):
                print(f"  {row[0]:20s} support={row[1]:7s} "
                      f"txn={row[3]:3s} xa={row[4]:3s} savepoints={row[5]}")

        if args.table:
            cur.execute("""SELECT ENGINE, TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH
                           FROM information_schema.TABLES
                           WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s""",
                        (db, args.table))
            r = cur.fetchone()
            if r:
                print(f"\n=== table {args.table} ===")
                print(f"  engine     = {r[0]}")
                print(f"  rows ~=    = {r[1]}")
                print(f"  data bytes = {r[2]}")
                print(f"  idx  bytes = {r[3]}")
            else:
                print(f"\n=== table {args.table}: NOT FOUND ===")

    print()
    print(f"SERVER_FLAVOR: {flavor}  VERSION: {version}  DEFAULT_ENGINE: {default_engine}")
    sys.exit(0)


if __name__ == '__main__':
    main()
