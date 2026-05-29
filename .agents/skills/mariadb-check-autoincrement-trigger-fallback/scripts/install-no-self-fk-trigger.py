#!/usr/bin/env python3
"""
install-no-self-fk-trigger.py - Idempotently install BEFORE INSERT and
BEFORE UPDATE triggers that prevent a self-referencing FK column from
pointing at the row's own primary key.

WHY: MariaDB / MySQL CHECK constraints CANNOT reference AUTO_INCREMENT
columns (error 1901, misleadingly worded). For chart-of-account style
parent_id FKs where the PK is AUTO_INCREMENT, a BEFORE INSERT + BEFORE
UPDATE trigger pair with SIGNAL SQLSTATE '45000' is the standard
fallback. See SKILL.md for the full pitfall write-up.

Inputs:
    --secrets <path>
    --table   <name>           e.g. accounts
    --pk-col  <name>           e.g. account_id    (the AUTO_INCREMENT PK)
    --parent-col <name>        e.g. parent_account_id
    --trigger-prefix <name>    default: trg_<table>_no_self_parent

Behavior: DROPs any pre-existing triggers with the chosen names, then
CREATEs the INS / UPD pair. Always emits the final SHOW TRIGGERS row
for confirmation.

Exit codes:
    0  both triggers installed
    2  config / connection / SQL error
"""
import argparse, sys

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
    ap.add_argument("--table", required=True)
    ap.add_argument("--pk-col", required=True)
    ap.add_argument("--parent-col", required=True)
    ap.add_argument("--trigger-prefix", default=None)
    a = ap.parse_args()

    prefix = a.trigger_prefix or f"trg_{a.table}_no_self_parent"
    ins_name = f"{prefix}_ins"
    upd_name = f"{prefix}_upd"
    msg = f"{a.parent_col} must not equal {a.pk_col} (self-reference forbidden)"

    try:
        import pymysql
    except ImportError:
        print("ERROR: pymysql not installed", file=sys.stderr); sys.exit(2)

    s = load_secrets(a.secrets)
    try:
        conn = pymysql.connect(host=s["DB_HOST"], user=s["DB_USER"],
                               password=s["DB_PASSWORD"], db=s["DB_NAME"],
                               autocommit=True, charset="utf8mb4")
    except Exception as e:
        print(f"ERROR: connect failed: {e}", file=sys.stderr); sys.exit(2)

    cur = conn.cursor()
    try:
        for name in (ins_name, upd_name):
            cur.execute(f"DROP TRIGGER IF EXISTS {name}")
            print(f"DROP TRIGGER IF EXISTS {name}: ok")

        cur.execute(f"""
            CREATE TRIGGER {ins_name}
            BEFORE INSERT ON {a.table}
            FOR EACH ROW
            BEGIN
              IF NEW.{a.parent_col} IS NOT NULL AND NEW.{a.parent_col} = NEW.{a.pk_col} THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '{msg}';
              END IF;
            END
        """)
        print(f"CREATE TRIGGER {ins_name}: ok")

        cur.execute(f"""
            CREATE TRIGGER {upd_name}
            BEFORE UPDATE ON {a.table}
            FOR EACH ROW
            BEGIN
              IF NEW.{a.parent_col} IS NOT NULL AND NEW.{a.parent_col} = NEW.{a.pk_col} THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '{msg}';
              END IF;
            END
        """)
        print(f"CREATE TRIGGER {upd_name}: ok")

        cur.execute(f"SHOW TRIGGERS LIKE '{a.table}'")
        for row in cur.fetchall():
            print(f"  {row[0]}  {row[1]} {row[2]}")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr); sys.exit(2)
    finally:
        cur.close(); conn.close()

if __name__ == "__main__":
    main()
