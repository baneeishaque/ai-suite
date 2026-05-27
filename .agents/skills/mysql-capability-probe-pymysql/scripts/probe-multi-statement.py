#!/usr/bin/env python3
"""
probe-multi-statement.py — Probe a MySQL server for CLIENT_MULTI_STATEMENTS support.

Sends two SELECT statements in a single execute() with the MULTI_STATEMENTS
client flag set. Prints a single deterministic verdict line on stdout:

    MULTI_STATEMENT_SUPPORTED: True   <raw-result-tuples>
    MULTI_STATEMENT_SUPPORTED: False  <exception-class> <message>

Exit code: 0 on supported, 1 on not-supported, 2 on configuration error.

Usage:
    probe-multi-statement.py --secrets <path-to-act.secrets-style-file>

Secrets file format (KEY=VALUE per line, '#' comments allowed):
    DB_HOST=...
    DB_USER=...
    DB_PASSWORD=...
    DB_NAME=...
    DB_PORT=3306   # optional, defaults to 3306
"""

import argparse
import sys


def parse_secrets(path):
    secrets = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, _, v = line.partition('=')
            secrets[k.strip()] = v.strip()
    return secrets


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--secrets', required=True,
                    help='Path to KEY=VALUE secrets file (act.secrets style).')
    args = ap.parse_args()

    try:
        import pymysql  # type: ignore
    except ImportError:
        print("PROBE_CONFIG_ERROR: pymysql not installed. "
              "Install via the direct mise python pip "
              "(see mise-tool-management Layer 5).", file=sys.stderr)
        sys.exit(2)

    try:
        s = parse_secrets(args.secrets)
    except OSError as e:
        print(f"PROBE_CONFIG_ERROR: cannot read secrets: {e}", file=sys.stderr)
        sys.exit(2)

    required = ('DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME')
    missing = [k for k in required if k not in s]
    if missing:
        print(f"PROBE_CONFIG_ERROR: missing keys in secrets: {missing}", file=sys.stderr)
        sys.exit(2)

    conn = pymysql.connect(
        host=s['DB_HOST'],
        port=int(s.get('DB_PORT', '3306')),
        user=s['DB_USER'],
        password=s['DB_PASSWORD'],
        database=s['DB_NAME'],
        client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
    )
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1+1 AS a; SELECT 2+2 AS b;")
        results = [cur.fetchall()]
        while cur.nextset():
            results.append(cur.fetchall())
        if len(results) >= 2:
            print(f"MULTI_STATEMENT_SUPPORTED: True  {results}")
            sys.exit(0)
        else:
            print(f"MULTI_STATEMENT_SUPPORTED: False  "
                  f"only_one_result_set  {results}")
            sys.exit(1)
    except Exception as e:
        print(f"MULTI_STATEMENT_SUPPORTED: False  {type(e).__name__}  {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
