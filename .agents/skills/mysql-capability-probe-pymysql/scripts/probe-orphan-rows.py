#!/usr/bin/env python3
"""
probe-orphan-rows.py — Enumerate the ACTUAL orphan rows for one or more
proposed foreign-key relationships.

Sister of `probe-fk-readiness.py`. That probe reports orphan COUNTS — useful
to decide "are we FK-ready yet?". This probe reports orphan ROWS — useful
to actually fix them (delete, repoint, or create the missing parent).

Treats both `IS NULL` and `= 0` as "no parent claimed", consistent with
the legacy convention seen in the Account-Ledger schema where 0 was used
as a sentinel before NULL became standard. Use `--strict-null` to opt out
and only treat `IS NULL` as no-parent.

For each --check, emits the COUNT plus up to --limit orphan rows showing
the columns named in --cols (defaults to the FK column plus the child
table primary key when discoverable).

Inputs:
    --secrets <path>
    --check  <child_table>.<child_col>=<parent_table>.<parent_col>   (repeatable)
    --cols   <table>:<csv-columns>                  (repeatable, optional)
    --limit  N                                      (default: 20)
    --strict-null                                   (default: 0 ALSO treated)

Output (stdout): per --check section showing total orphan count and the
first --limit orphan rows. Terminal line:
    --- ORPHAN_TOTAL: <N> across <K> check(s) ---

Exit code:
    0  zero orphans across all checks
    1  at least one orphan found (informational, not an error)
    2  configuration / connection error
"""
import argparse
import sys


def parse_secrets(path):
    out = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip()
    return out


def parse_check(raw):
    if "=" not in raw:
        raise ValueError(f"--check must be CHILD.COL=PARENT.COL: {raw!r}")
    left, _, right = raw.partition("=")
    if "." not in left or "." not in right:
        raise ValueError(f"--check side missing dot: {raw!r}")
    ct, _, cc = left.partition(".")
    pt, _, pc = right.partition(".")
    return ct.strip(), cc.strip(), pt.strip(), pc.strip()


def parse_cols(raw):
    if ":" not in raw:
        raise ValueError(f"--cols must be TABLE:col1,col2,...: {raw!r}")
    t, _, csv = raw.partition(":")
    return t.strip(), [c.strip() for c in csv.split(",") if c.strip()]


def discover_pk(cur, db, table):
    cur.execute(
        "SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND CONSTRAINT_NAME=%s "
        "ORDER BY ORDINAL_POSITION",
        (db, table, "PRIMARY"),
    )
    return [r[0] for r in cur.fetchall()]


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--secrets", required=True)
    ap.add_argument(
        "--check", action="append", required=True,
        metavar="CHILD.COL=PARENT.COL",
        help="Repeatable. Declare each FK relationship to enumerate orphans for.",
    )
    ap.add_argument(
        "--cols", action="append", default=[],
        metavar="TABLE:col1,col2,...",
        help="Repeatable. Override columns displayed per child table.",
    )
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument(
        "--strict-null", action="store_true",
        help="Only IS NULL is no-parent. Default also treats =0.",
    )
    args = ap.parse_args()

    try:
        checks = [parse_check(c) for c in args.check]
        col_overrides = dict(parse_cols(c) for c in args.cols)
    except ValueError as e:
        print(f"PROBE_CONFIG_ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        import pymysql  # type: ignore
    except ImportError:
        print("PROBE_CONFIG_ERROR: pymysql not installed", file=sys.stderr)
        sys.exit(2)

    s = parse_secrets(args.secrets)
    for k in ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"):
        if k not in s:
            print(f"PROBE_CONFIG_ERROR: missing {k}", file=sys.stderr)
            sys.exit(2)

    db = s["DB_NAME"]
    grand_total = 0

    conn = pymysql.connect(
        host=s["DB_HOST"], port=int(s.get("DB_PORT", "3306")),
        user=s["DB_USER"], password=s["DB_PASSWORD"], database=db,
    )
    try:
        with conn.cursor() as cur:
            for ct, cc, pt, pc in checks:
                print(f"=== {ct}.{cc} -> {pt}.{pc} ===")

                if args.strict_null:
                    no_parent_pred = f"x.`{cc}` IS NULL"
                else:
                    no_parent_pred = f"(x.`{cc}` IS NULL OR x.`{cc}` = 0)"

                orphan_where = (
                    f"NOT ({no_parent_pred}) "
                    f"AND NOT EXISTS("
                    f"  SELECT 1 FROM `{pt}` p WHERE p.`{pc}` = x.`{cc}`)"
                )

                cur.execute(f"SELECT COUNT(*) FROM `{ct}` x WHERE {orphan_where}")
                total = cur.fetchone()[0]
                grand_total += total
                print(f"  total = {total}")

                if total == 0:
                    print()
                    continue

                display = col_overrides.get(ct)
                if not display:
                    pk = discover_pk(cur, db, ct)
                    display = list(dict.fromkeys(pk + [cc]))

                col_sql = ", ".join(f"`{c}`" for c in display)
                cur.execute(
                    f"SELECT {col_sql} FROM `{ct}` x WHERE {orphan_where} "
                    f"ORDER BY {col_sql} LIMIT %s",
                    (args.limit,),
                )
                rows = cur.fetchall()
                print(f"  first {len(rows)} orphan row(s): {display}")
                for r in rows:
                    print(f"    {r}")
                print()
    finally:
        conn.close()

    print(f"--- ORPHAN_TOTAL: {grand_total} across {len(checks)} check(s) ---")
    sys.exit(0 if grand_total == 0 else 1)


if __name__ == "__main__":
    main()
