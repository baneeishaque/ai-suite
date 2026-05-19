#!/usr/bin/env python3
"""
edit-entry.py — Add, replace, or migrate a single chat.tools.terminal.autoApprove entry.

Part of the vscode-terminal-autoapprove-audit skill.
See ../SKILL.md §7.4 for usage context.

Modes:
    --add      Insert a new entry at the tail with {approve:true, matchCommandLine:true}.
    --replace  Replace an existing entry's KEY in place (value preserved, position preserved).
    --delete   Remove an existing entry by exact key.

Usage:
    # Add a new anchored entry
    python3 edit-entry.py --settings <path> --add --key '/^echo( [^;&|<>$`()]*)?$/'

    # Migrate loose prefix to anchored regex (position preserved)
    python3 edit-entry.py --settings <path> --replace \
      --old-key '"command": true'-style-bare-form  \
      --new-key '/^command -v [A-Za-z0-9_.+-]+$/'

    # Delete one entry by exact key
    python3 edit-entry.py --settings <path> --delete --key '<full key>'

Formatting:
    Writes JSON with indent=4 (matches the convention of the target file).
    For non-default indentation profiles, run vscode-settings-indent-override
    afterwards — see SKILL.md §3.1.

Exit codes:
    0  success   1  key collision / missing   2  argument error
"""

import argparse
import collections
import json
import sys


def load_data(path: str):
    with open(path, encoding="utf-8") as fp:
        return json.load(fp, object_pairs_hook=collections.OrderedDict)


def save_data(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=4)
        fp.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Edit a single autoApprove entry.")
    parser.add_argument("--settings", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--add", action="store_true")
    mode.add_argument("--replace", action="store_true")
    mode.add_argument("--delete", action="store_true")
    parser.add_argument("--key", help="Key for --add or --delete")
    parser.add_argument("--old-key", help="Existing key for --replace")
    parser.add_argument("--new-key", help="Replacement key for --replace")
    args = parser.parse_args()

    data = load_data(args.settings)
    aa = data.setdefault("chat.tools.terminal.autoApprove",
                         collections.OrderedDict())
    approve = {"approve": True, "matchCommandLine": True}
    before = len(aa)

    if args.add:
        if not args.key:
            print("ERROR: --add requires --key", file=sys.stderr); return 2
        if args.key in aa:
            print(f"ERROR: key already present: {args.key[:80]!r}", file=sys.stderr)
            return 1
        aa[args.key] = approve

    elif args.replace:
        if not (args.old_key and args.new_key):
            print("ERROR: --replace requires --old-key and --new-key", file=sys.stderr)
            return 2
        if args.old_key not in aa:
            print(f"ERROR: old key not found: {args.old_key[:80]!r}", file=sys.stderr)
            return 1
        if args.new_key != args.old_key and args.new_key in aa:
            print(f"ERROR: new key collides: {args.new_key[:80]!r}", file=sys.stderr)
            return 1
        new_aa = collections.OrderedDict()
        for k, v in aa.items():
            if k == args.old_key:
                new_aa[args.new_key] = approve  # value normalised
            else:
                new_aa[k] = v
        data["chat.tools.terminal.autoApprove"] = new_aa

    else:  # delete
        if not args.key:
            print("ERROR: --delete requires --key", file=sys.stderr); return 2
        if args.key not in aa:
            print(f"ERROR: key not found: {args.key[:80]!r}", file=sys.stderr)
            return 1
        del aa[args.key]

    save_data(args.settings, data)
    after = len(data["chat.tools.terminal.autoApprove"])
    mode_str = "add" if args.add else "replace" if args.replace else "delete"
    print(f"OK ({mode_str}). entries: {before} -> {after}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
