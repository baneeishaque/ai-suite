#!/usr/bin/env python3
"""Discover the valid option values of a single-select custom field in Jira.

acli has NO command to list a custom field's options, and `acli jira field`
only creates/updates/deletes fields. So we infer the option set with JQL:

  1. "<FIELD> IS NOT EMPTY"  -> count of every item that has a value (the
     universe). A JQL error "the option 'X' for field 'Y' does not exist"
     means X is NOT a real option -- use that feedback to correct guesses.
  2. "<FIELD> = '<CANDIDATE>'"  -> a known-good value returns a count > 0 and
     a known-bad value returns the "does not exist" error.
  3. Once candidate values are known, "<FIELD> NOT IN (a, b, c)" reveals the
     remaining items; `view` one of them to read the exact string.

Usage:
    python3 discover-select-options.py --field "Release Status" [--guess Ready for release Not ready Released]
    python3 discover-select-options.py --field "Release Status" --field-id customfield_10252

Tips:
  - Pass --field-id to skip the field-name/space quoting guesswork; acli
    itself strips spaces from --fields, so always quote the field name in JQL.
  - Always pass JQL to acli as ONE argv token (this script uses a subprocess
    arg list, never a shell string).
"""
import argparse
import json
import re
import subprocess
import sys

# Heuristic starting guesses for common release/status-like fields.
DEFAULT_GUESSES = [
    "Ready for release", "Ready for Release", "Not ready", "Released",
    "Not applicable", "N/A", "In Progress", "Done", "Blocked", "On hold",
    "Pending", "Testing", "QA", "UAT", "Deployed", "Ready",
]


def run(jql: str) -> tuple:
    """Run a search count; return (count_or_None, stderr)."""
    try:
        out = subprocess.run(
            ["acli", "jira", "workitem", "search", "--jql", jql, "--count"],
            capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError as e:
        return None, e.stderr
    m = re.search(r"Number of work items in the search:\s*(\d+)", out)
    return (int(m.group(1)) if m else None), ""


def universe(field: str) -> int:
    c, err = run(f'"{field}" IS NOT EMPTY')
    if c is None:
        c, _ = run(f"{field} IS NOT EMPTY")
    return c


def probe(field: str, value: str) -> str:
    """Return 'valid' | 'empty' | 'invalid'."""
    c, err = run(f'"{field}" = "{value}"')
    if c is None:
        if "does not exist" in err:
            return "invalid"
        raise RuntimeError(err)
    return "valid" if c > 0 else "empty"


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--field", required=True, help="Field name, e.g. 'Release Status'")
    ap.add_argument("--field-id", default=None,
                    help="Custom field ID if known (skips name guessing)")
    ap.add_argument("--guess", nargs="*", default=DEFAULT_GUESSES,
                    help="Candidate option strings to test")
    args = ap.parse_args()

    field = args.field
    print(f"Universe ('{field}' IS NOT EMPTY): {universe(field)} items", file=sys.stderr)

    known = []
    for g in args.guess:
        verdict = probe(field, g)
        if verdict == "valid":
            known.append(g)
            print(f"  VALID   {g}")
        elif verdict == "invalid":
            print(f"  invalid {g}")
        # 'empty' = valid option but no items currently use it; keep it.

    # Reveal stragglers: anything NOT in the known set.
    if known:
        not_in = ", ".join(f'"{v}"' for v in known)
        c, err = run(f'"{field}" IS NOT EMPTY AND "{field}" NOT IN ({not_in})')
        print(f"Items NOT in {{ {', '.join(known)} }}: {c}", file=sys.stderr)
        if c and c > 0:
            print("To read the exact remaining option string(s):", file=sys.stderr)
            print(f"  acli jira workitem search --jql '{field} IS NOT EMPTY AND {field}"
                  f" NOT IN ({not_in})' --fields key --limit 3", file=sys.stderr)
            print("  then: acli jira workitem view <KEY> --fields '*all' --json", file=sys.stderr)

    print("\nDiscovered options:", ", ".join(known) if known else "(none)")


if __name__ == "__main__":
    main()
