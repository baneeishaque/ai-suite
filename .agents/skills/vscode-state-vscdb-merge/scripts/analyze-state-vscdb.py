#!/usr/bin/env python3
"""Compare and optionally merge VS Code state.vscdb SQLite databases
between two Git refs.

Tier-1 (Python 3.9+, stdlib only).  Read-only by default (analysis mode);
--merge REQUIRES explicit user authorization.
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import tempfile


def _extract_db(repo: str, ref: str, db_relpath: str) -> str:
    """Extract state.vscdb from a Git ref into a temp file.

    Returns the temp file path.
    """
    cmd = ["git", "-C", repo, "show", f"{ref}:{db_relpath}"]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".state.vscdb")
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        tmp.write(result.stdout)
        tmp.close()
        return tmp.name
    except subprocess.CalledProcessError as e:
        sys.stderr.write(
            f"ERROR: 'git show {ref}:{db_relpath}' failed (exit {e.returncode})\n"
        )
        sys.exit(2)
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(2)


def _read_db(path: str) -> dict:
    """Read ItemTable from a state.vscdb file into {key: value} dict."""
    d = {}
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        cur = conn.execute("SELECT key, value FROM ItemTable")
        for row in cur:
            d[row[0]] = row[1]
        conn.close()
    except sqlite3.Error as e:
        sys.stderr.write(f"ERROR: SQLite read failed on {path}: {e}\n")
        sys.exit(2)
    return d


def _resolve_ref(repo: str, stash_spec: str | None, ref_a: str | None) -> str:
    """Resolve the user-supplied --stash or --ref-a to a canonical Git ref."""
    if stash_spec is not None:
        if stash_spec.startswith("stash@{"):
            return stash_spec
        if stash_spec.isdigit():
            return f"stash@{{{stash_spec}}}"
        # Try message-substring match
        try:
            result = subprocess.run(
                ["git", "-C", repo, "stash", "list"],
                capture_output=True, text=True, check=True,
            )
            lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
            matches = [l for l in lines if stash_spec in l]
            if not matches:
                sys.stderr.write(
                    f"ERROR: no stash matches substring {stash_spec!r}\n"
                )
                sys.exit(2)
            if len(matches) > 1:
                sys.stderr.write(
                    f"ERROR: {len(matches)} stashes match {stash_spec!r}:\n"
                )
                for m in matches:
                    sys.stderr.write(f"  {m}\n")
                sys.exit(2)
            return matches[0].split(":")[0].strip()
        except subprocess.CalledProcessError:
            sys.stderr.write("ERROR: git stash list failed\n")
            sys.exit(2)
    if ref_a is not None:
        return ref_a
    sys.stderr.write("ERROR: one of --stash or --ref-a is required\n")
    sys.exit(2)


def _report_text(stash_keys: set, head_keys: set,
                 stash_dict: dict, head_dict: dict) -> str:
    """Build a human-readable analysis report."""
    only_stash = stash_keys - head_keys
    only_head = head_keys - stash_keys
    common = stash_keys & head_keys
    same_vals = {k for k in common if stash_dict[k] == head_dict[k]}
    diff_vals = common - same_vals

    lines = []
    lines.append(f"Keys only in Ref A (stash):   {len(only_stash)}")
    lines.append(f"Keys only in Ref B (HEAD):    {len(only_head)}")
    lines.append(f"Keys in both, same value:     {len(same_vals)}")
    lines.append(f"Keys in both, DIFFERENT value: {len(diff_vals)}")
    lines.append("")

    if only_stash:
        lines.append("--- Keys only in Ref A (stash) ---")
        for k in sorted(only_stash)[:50]:
            v = stash_dict[k]
            lines.append(f"  {k}")
        if len(only_stash) > 50:
            lines.append(f"  ... and {len(only_stash) - 50} more")

    if only_head:
        lines.append("--- Keys only in Ref B (HEAD) ---")
        for k in sorted(only_head)[:30]:
            lines.append(f"  {k}")
        if len(only_head) > 30:
            lines.append(f"  ... and {len(only_head) - 30} more")

    if diff_vals:
        lines.append("--- Keys with DIFFERENT values ---")
        for k in sorted(diff_vals)[:30]:
            a_val = stash_dict[k]
            b_val = head_dict[k]
            a_preview = a_val[:80] + "..." if len(a_val) > 80 else a_val
            b_preview = b_val[:80] + "..." if len(b_val) > 80 else b_val
            lines.append(f"  {k}:")
            lines.append(f"    Ref A: {a_preview}")
            lines.append(f"    Ref B: {b_preview}")
        if len(diff_vals) > 30:
            lines.append(f"  ... and {len(diff_vals) - 30} more")

    return "\n".join(lines)


def _report_json(stash_keys: set, head_keys: set,
                 stash_dict: dict, head_dict: dict) -> str:
    """Build a JSON analysis report."""
    only_stash = sorted(stash_keys - head_keys)
    only_head = sorted(head_keys - stash_keys)
    common = sorted(stash_keys & head_keys)
    same_vals = [k for k in common if stash_dict[k] == head_dict[k]]
    diff_vals = [
        {"key": k, "ref_a_value": stash_dict[k], "ref_b_value": head_dict[k]}
        for k in common if stash_dict[k] != head_dict[k]
    ]
    report = {
        "ref_a_keys_total": len(stash_keys),
        "ref_b_keys_total": len(head_keys),
        "keys_only_in_ref_a": only_stash,
        "keys_only_in_ref_b": only_head,
        "keys_common_same_value": same_vals,
        "keys_common_different_value": diff_vals,
    }
    return json.dumps(report, indent=2)


def _merge_dbs(head_path: str, output_path: str,
               stash_only_keys: set, stash_dict: dict) -> str:
    """Merge stash-only keys into a copy of HEAD's database.

    Creates a new database at output_path with all HEAD keys PLUS
    stash-only keys added.  Original HEAD database is NOT modified.
    """
    import shutil
    shutil.copy2(head_path, output_path)

    conn = sqlite3.connect(output_path)
    try:
        inserted = 0
        for k in stash_only_keys:
            conn.execute(
                "INSERT OR IGNORE INTO ItemTable (key, value) VALUES (?, ?)",
                (k, stash_dict[k]),
            )
            inserted += 1
        conn.commit()

        cur = conn.execute("SELECT COUNT(*) FROM ItemTable")
        final_count = cur.fetchone()[0]
        conn.close()
        return final_count
    except sqlite3.Error as e:
        conn.close()
        os.unlink(output_path)
        sys.stderr.write(f"ERROR: merge failed: {e}\n")
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze VS Code state.vscdb between two Git refs"
    )
    parser.add_argument("--repo", required=True, help="Path to Git repository")
    parser.add_argument("--db-path", required=True,
                        help="Relative path to state.vscdb in the repo")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--stash", help="Stash specifier (index, stash@{N}, or message substring)")
    group.add_argument("--ref-a", help="Git ref for the source database")
    parser.add_argument("--ref-b", default="HEAD", help="Git ref for the target database (default: HEAD)")
    parser.add_argument("--merge", action="store_true",
                        help="Apply merge (insert stash-only keys into HEAD copy) — requires explicit user auth")
    parser.add_argument("--output", help="Output path for merged database (default: <cwd>/HEAD-merged.state.vscdb)")
    parser.add_argument("--json", action="store_true", help="Emit JSON report instead of human-readable text")
    args = parser.parse_args()

    # Resolve refs
    ref_a = _resolve_ref(args.repo, args.stash, args.ref_a)
    ref_b = args.ref_b

    # Extract databases
    a_path = _extract_db(args.repo, ref_a, args.db_path)
    b_path = _extract_db(args.repo, ref_b, args.db_path)

    # Read both
    a_dict = _read_db(a_path)
    b_dict = _read_db(b_path)
    a_keys = set(a_dict.keys())
    b_keys = set(b_dict.keys())

    # Report
    if args.json:
        print(_report_json(a_keys, b_keys, a_dict, b_dict))
    else:
        print(_report_text(a_keys, b_keys, a_dict, b_dict))

    # Merge (optional, requires user auth)
    if args.merge:
        stash_only = a_keys - b_keys
        if not stash_only:
            print("\n[NO MERGE NEEDED] No stash-only keys to insert.")
            sys.exit(0)
        output = args.output or os.path.join(os.getcwd(), "HEAD-merged.state.vscdb")
        final_count = _merge_dbs(b_path, output, stash_only, a_dict)
        print(f"\n[MERGE COMPLETE] Merged database written to: {output}")
        print(f"  HEAD keys:            {len(b_keys)}")
        print(f"  Stash-only keys added: {len(stash_only)}")
        print(f"  Final key count:       {final_count}")

    # Clean up temp files
    os.unlink(a_path)
    os.unlink(b_path)


if __name__ == "__main__":
    main()
