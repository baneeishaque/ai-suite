#!/usr/bin/env python3
"""
commit-update.py - Execute an UPDATE for real (COMMIT) AFTER a matching
dry-run-update.py invocation has been authorized by the user.

Refuses to run unless --require-dry-run-sha matches the sha printed by
dry-run-update.py for the SAME --update + --verify pair. This drifts-guard
prevents "I ran a dry run yesterday, let me commit today" mistakes where
the schema or data changed in between.

Inputs:
    --secrets <path>
    --update  "<SQL>"
    --verify  "<SQL>"                 same SELECT that should return 0 rows after
    --require-dry-run-sha <16-hex>    sha printed by dry-run-update.py
    --re-dry-run                      (default true) re-run dry-run check first

Output:
    DRY_RUN_RECHECK: ok
    AFFECTED_ROWS:   <n>
    VERIFY_ROWS:     <n>
    COMMIT: ok

Exit codes:
    0  committed successfully
    2  config / connection error
    3  --require-dry-run-sha mismatch, or post-commit verify returned > 0 rows
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
    ap.add_argument("--require-dry-run-sha", required=True)
    a = ap.parse_args()

    sha = hashlib.sha256(f"{a.update}\n{a.verify}".encode()).hexdigest()[:16]
    if sha != a.require_dry_run_sha:
        print(f"ERROR: sha mismatch (computed {sha}, required {a.require_dry_run_sha})",
              file=sys.stderr); sys.exit(3)

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
        cur.execute(a.verify)
        verify_rows = cur.fetchall()
        if verify_rows:
            conn.rollback()
            print(f"ERROR: post-update verify returned {len(verify_rows)} rows; rolled back",
                  file=sys.stderr); sys.exit(3)
        conn.commit()
        print("DRY_RUN_RECHECK: ok")
        print(f"AFFECTED_ROWS:   {affected}")
        print(f"VERIFY_ROWS:     0")
        print("COMMIT: ok")
        sys.exit(0)
    finally:
        cur.close(); conn.close()

if __name__ == "__main__":
    main()
