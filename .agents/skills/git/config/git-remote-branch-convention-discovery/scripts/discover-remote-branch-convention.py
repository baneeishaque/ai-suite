#!/usr/bin/env python3
"""Infer a remote's branch naming / grouping convention from its live heads (READ-ONLY).

Enumerates `git ls-remote --heads <remote>` and reports the grouping prefixes the
remote actually follows, their counts, and the outliers that break the dominant
convention. This exists because convention-ownership skills state a convention as an
axiom (e.g. "the personal/ prefix is required") without ever teaching the reader how
to DISCOVER the convention for a remote whose scheme they do not already know.

Read-only contract: this script NEVER fetches, NEVER pushes, and NEVER mutates any
ref, index, or working tree. It only reads.

Tier: Tier 1 (Python) per scripting-language-selection-rules.md section 3 (Tier 1 is
the default) and section 4 (string grouping + JSON report assembly) -- stdlib only,
no CPU bottleneck, no ecosystem mandate.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import subprocess
import sys


def run_git(args, cwd=None):
    try:
        proc = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            env={**os.environ, "PAGER": "cat"},
        )
    except FileNotFoundError:
        return 127, "", "git not found on PATH"
    return proc.returncode, proc.stdout, proc.stderr


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Infer a remote's branch naming/grouping convention from live heads."
    )
    ap.add_argument("--repo", default=".", help="Repository or linked-worktree git dir.")
    ap.add_argument("--remote", required=True, help="Remote name whose convention to infer.")
    ap.add_argument("--json", action="store_true", help="Emit JSON (default is JSON).")
    args = ap.parse_args()

    code, out, err = run_git(["ls-remote", "--heads", args.remote], cwd=args.repo)
    if code != 0:
        print("error: remote not reachable: %s (%s)" % (args.remote, err.strip()[:200]), file=sys.stderr)
        return 2

    names = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].startswith("refs/heads/"):
            names.append(parts[1][len("refs/heads/"):])
    names.sort()

    buckets = collections.OrderedDict()
    ungrouped = []
    for name in names:
        if "/" in name:
            prefix = name.split("/", 1)[0] + "/"
            buckets.setdefault(prefix, []).append(name)
        else:
            ungrouped.append(name)

    groupings = []
    for prefix, members in buckets.items():
        groupings.append({"prefix": prefix, "count": len(members), "examples": members[:3]})
    groupings.sort(key=lambda g: (-g["count"], g["prefix"]))

    dominant = groupings[0]["prefix"] if groupings else None

    payload = {
        "remote": args.remote,
        "total_heads": len(names),
        "groupings": groupings,
        "dominant_prefix": dominant,
        "ungrouped": ungrouped,
        "outliers": ungrouped if dominant else [],
        "recommended_name_hint": ("%s<purpose>" % dominant) if dominant else "<branch-name>",
        "heads": names,
        "caveat": (
            "Convention inferred from live remote heads at probe time. A remote with "
            "no grouping prefix yields dominant_prefix=null and no recommendation; "
            "re-verify with a fresh probe before naming a branch."
        ),
    }

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())