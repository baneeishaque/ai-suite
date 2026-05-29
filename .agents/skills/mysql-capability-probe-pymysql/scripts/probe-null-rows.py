#!/usr/bin/env python3
"""
probe-null-rows.py — Enumerate the ACTUAL rows whose values in one or more
columns are "no value claimed" (NULL or sentinel 0).

Sister of `probe-orphan-rows.py`. That probe walks FK relationships and
reports rows whose FK value has no matching parent. This probe is
single-sided: it does NOT join to a parent — it simply lists rows whose
value in the named column is NULL or 0, which is what you usually need
to inspect BEFORE running a NULL-migration / NOT-NULL ALTER, or before
choosing a default to backfill.

Default semantics treat both `IS NULL` and `= 0` as "no value claimed",
consistent with the legacy convention seen in the Account-Ledger schema
where 0 was used as a sentinel before NULL became standard. Use
`--strict-null` to opt out and only treat `IS NULL` as no-value.

For each --check, emits the COUNT plus up to --limit matching rows
showing the columns named in --cols (defaults to the table primary key
plus the checked column when discoverable).

Inputs:
    --secrets <path>
    --check  <table>.<col>                          (repeatable)
    --cols   <table>:<csv-columns>                  (repeatable, optional)
    --limit  N                                      (default: 20)
    --strict-null                                   (default: 0 ALSO counted)

Output (stdout): per --check section showing total no-value count and the
first --limit matching rows. Terminal line:
    --- NULL_TOTAL: <N> across <K> check(s) ---

Exit code:
    0  zero no-value rows across all checks
    1  at least one no-value row found (informational, not an error)
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
    if "." not in raw:
        raise ValueError(f"--check must be TABLE.COL: {raw!r}")
    t, _, c = raw.partition(".")
    t, c = t.strip(), c.strip()
    if not t or not c:
        raise ValueError(f"--check has empty side: {raw!r}")
    return t, c


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
        metavar="TABLE.COL",
        help="Repeatable. Declare each column to enumerate no-value rows for.",
    )
    ap.add_argument(
        "--cols", action="append", default=[],
        metavar="TABLE:col1,col2,...",
        help="Repeatable. Override columns displayed per table.",
    )
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument(
        "--strict-null", action="store_true",
        help="Only IS NULL is no-value. Default also treats =0.",
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
            for t, c in checks:
                print(f"=== {t}.{c} ===")

                if args.strict_null:
                    no_value_pred = f"x.`{c}` IS NULL"
                else:
                    no_value_pred = f"(x.`{c}` IS NULL OR x.`{c}` = 0)"

                cur.execute(f"SELECT COUNT(*) FROM `{t}` x WHERE {no_value_pred}")
                total = cur.fetchone()[0]
                grand_total += total
                print(f"  total = {total}")

                if total == 0:
                    print()
                    continue

                display = col_overrides.get(t)
                if not display:
                    pk = discover_pk(cur, db, t)
                    display = list(dict.fromkeys(pk + [c]))

                col_sql = ", ".join(f"`{col}`" for col in display)
                cur.execute(
                    f"SELECT {col_sql} FROM `{t}` x WHERE {no_value_pred} "
                    f"ORDER BY {col_sql} LIMIT %s",
                    (args.limit,),
                )
                rows = cur.fetchall()
                print(f"  first {len(rows)} no-value row(s): {display}")
                for r in rows:
                    print(f"    {r}")
                print()
    finally:
        conn.close()

    print(f"--- NULL_TOTAL: {grand_total} across {len(checks)} check(s) ---")
    sys.exit(0 if grand_total == 0 else 1)


if __name__ == "__main__":
    main()
