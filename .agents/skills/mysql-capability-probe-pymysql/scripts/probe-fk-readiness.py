#!/usr/bin/env python3
"""
probe-fk-readiness.py — Determine whether a set of tables is ready for the
addition of foreign-key constraints.

For each target table, reports:
    - storage ENGINE (FKs require InnoDB; MyISAM silently drops FK clauses)
    - existing FK constraints
    - column nullability for the configured FK columns
    - top-level (NULL) row count for parent-pointer columns
    - orphan row counts: rows whose FK value does not exist in the parent table

This is the prerequisite check before issuing `ALTER TABLE … ADD FOREIGN KEY`,
because that ALTER fails with ERROR 1452 when orphans exist.

Inputs:
    --secrets <path>
    --fk <child_table>.<child_col>=<parent_table>.<parent_col>   (repeatable)

Output (stdout): structured sections — `=== engines ===`, `=== existing FKs ===`,
`=== nullability ===`, `=== top-level counts ===`, `=== orphan counts ===`.
Terminal line:
    --- FK_READY: True   (engine=InnoDB AND orphans=0 across all FKs)
    --- FK_READY: False  (one or more blockers; see sections above)

Exit code:
    0  all configured FKs are ready to add (no blockers)
    1  at least one blocker
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


def parse_fk(raw):
    """child.col=parent.col -> (child_t, child_c, parent_t, parent_c)"""
    if '=' not in raw:
        raise ValueError(f"--fk must be CHILD.COL=PARENT.COL: {raw!r}")
    left, _, right = raw.partition('=')
    if '.' not in left or '.' not in right:
        raise ValueError(f"--fk side missing dot: {raw!r}")
    ct, _, cc = left.partition('.')
    pt, _, pc = right.partition('.')
    return ct.strip(), cc.strip(), pt.strip(), pc.strip()


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument('--secrets', required=True)
    ap.add_argument(
        '--fk', action='append', required=True,
        metavar='CHILD.COL=PARENT.COL',
        help='Repeatable. Declare each proposed FK relationship.',
    )
    args = ap.parse_args()

    try:
        fks = [parse_fk(f) for f in args.fk]
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

    db = s['DB_NAME']
    tables = sorted({t for ct, _, pt, _ in fks for t in (ct, pt)})

    blockers = 0
    conn = pymysql.connect(
        host=s['DB_HOST'], port=int(s.get('DB_PORT', '3306')),
        user=s['DB_USER'], password=s['DB_PASSWORD'], database=db,
    )
    try:
        with conn.cursor() as cur:
            print("=== engines ===")
            cur.execute(
                "SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES "
                "WHERE TABLE_SCHEMA=%s AND TABLE_NAME IN ("
                + ",".join(["%s"] * len(tables)) + ")",
                (db, *tables),
            )
            engines = {r[0]: r[1] for r in cur.fetchall()}
            for t in tables:
                eng = engines.get(t, "MISSING")
                tag = "" if eng == "InnoDB" else "  <-- BLOCKER (FKs need InnoDB)"
                if eng != "InnoDB":
                    blockers += 1
                print(f"  {t:30s} {eng}{tag}")

            print("\n=== existing FK constraints ===")
            cur.execute(
                "SELECT TABLE_NAME, CONSTRAINT_NAME, COLUMN_NAME, "
                "REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
                "FROM information_schema.KEY_COLUMN_USAGE "
                "WHERE TABLE_SCHEMA=%s AND REFERENCED_TABLE_NAME IS NOT NULL "
                "AND TABLE_NAME IN ("
                + ",".join(["%s"] * len(tables)) + ")",
                (db, *tables),
            )
            rows = cur.fetchall()
            if not rows:
                print("  (none)")
            for r in rows:
                print(f"  {r[0]}.{r[2]} -> {r[3]}.{r[4]}  ({r[1]})")

            print("\n=== column nullability ===")
            for ct, cc, _, _ in fks:
                cur.execute(
                    "SELECT IS_NULLABLE, COLUMN_TYPE "
                    "FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s",
                    (db, ct, cc),
                )
                row = cur.fetchone()
                if not row:
                    print(f"  {ct}.{cc:25s} MISSING")
                    blockers += 1
                else:
                    nul, typ = row
                    print(f"  {ct}.{cc:25s} nullable={nul:3s}  type={typ}")

            print("\n=== top-level (NULL parent) counts ===")
            for ct, cc, _, _ in fks:
                cur.execute(
                    f"SELECT COUNT(*) FROM `{ct}` WHERE `{cc}` IS NULL"
                )
                n = cur.fetchone()[0]
                print(f"  {ct}.{cc} IS NULL: {n}  "
                      f"(FKs do NOT validate NULL values)")

            print("\n=== orphan counts ===")
            for ct, cc, pt, pc in fks:
                cur.execute(
                    f"SELECT COUNT(*) FROM `{ct}` x "
                    f"WHERE x.`{cc}` IS NOT NULL "
                    f"  AND NOT EXISTS("
                    f"    SELECT 1 FROM `{pt}` p WHERE p.`{pc}` = x.`{cc}`)"
                )
                n = cur.fetchone()[0]
                tag = "" if n == 0 else "  <-- BLOCKER (cleanup required)"
                if n != 0:
                    blockers += 1
                print(f"  {ct}.{cc} -> {pt}.{pc}: {n} orphan(s){tag}")
    finally:
        conn.close()

    ready = blockers == 0
    print(f"\n--- FK_READY: {ready}  ({blockers} blocker(s)) ---")
    sys.exit(0 if ready else 1)


if __name__ == '__main__':
    main()
