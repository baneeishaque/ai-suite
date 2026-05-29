#!/usr/bin/env python3
"""
dry-run-update.py - Execute an UPDATE inside an explicit transaction,
report affected_rows and a verification SELECT, then ROLLBACK.

Use to PROVE an UPDATE statement does what you expect (and nothing more)
BEFORE letting commit-update.py run the production write.

Inputs:
    --secrets <path>      Env-format file with DB_HOST/DB_USER/DB_PASSWORD/DB_NAME
    --update  "<SQL>"     The UPDATE statement (no trailing ';')
    --verify  "<SQL>"     A SELECT that should return 0 rows AFTER the update
                          (e.g. the population that should have been migrated)
    --expect-rows N       Optional: assert affected_rows == N, else exit 3

Output:
    AFFECTED_ROWS: <n>
    VERIFY_ROWS:   <n>
    --- DRY_RUN_SHA: <sha256 of update+verify> ---  (consumed by commit-update.py)

Always issues ROLLBACK. Never commits.

Exit codes:
    0  dry run executed cleanly (affected_rows OK, verify returned 0)
    2  config / connection error
    3  --expect-rows mismatch or verify returned > 0 rows
"""
import argparse, hashlib, sys

def load_secrets(path):
    out = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip()
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--secrets", required=True)
    ap.add_argument("--update", required=True)
    ap.add_argument("--verify", required=True)
    ap.add_argument("--expect-rows", type=int, default=None)
    a = ap.parse_args()

    try:
        import pymysql
    except ImportError:
        print("ERROR: pymysql not installed", file=sys.stderr); sys.exit(2)

    s = load_secrets(a.secrets)
    try:
        conn = pymysql.connect(host=s["DB_HOST"], user=s["DB_USER"],
                               password=s["DB_PASSWORD"], db=s["DB_NAME"],
                               autocommit=False, charset="utf8mb4")
    except Exception as e:
        print(f"ERROR: connect failed: {e}", file=sys.stderr); sys.exit(2)

    cur = conn.cursor()
    try:
        cur.execute("START TRANSACTION")
        affected = cur.execute(a.update)
        print(f"AFFECTED_ROWS: {affected}")
        cur.execute(a.verify)
        verify_rows = cur.fetchall()
        print(f"VERIFY_ROWS:   {len(verify_rows)}")
        if verify_rows:
            for r in verify_rows[:10]:
                print(f"  {r}")
        conn.rollback()
        print("ROLLBACK: ok")

        if a.expect_rows is not None and affected != a.expect_rows:
            print(f"ERROR: expected {a.expect_rows} affected, got {affected}", file=sys.stderr)
            sys.exit(3)
        if verify_rows:
            print(f"ERROR: verify returned {len(verify_rows)} rows (expected 0)", file=sys.stderr)
            sys.exit(3)

        sha = hashlib.sha256(f"{a.update}\n{a.verify}".encode()).hexdigest()[:16]
        print(f"--- DRY_RUN_SHA: {sha} ---")
        sys.exit(0)
    finally:
        cur.close(); conn.close()

if __name__ == "__main__":
    main()
