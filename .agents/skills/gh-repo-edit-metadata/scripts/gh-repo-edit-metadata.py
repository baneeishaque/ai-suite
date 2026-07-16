#!/usr/bin/env python3
"""
gh-repo-edit-metadata.py — Tier 1 (Python) per scripting-language-selection-rules.md §2.3

Wrap `gh repo edit` for description and topic management. Accepts a description
string and repeatable --add-topic/--remove-topic flags. Outputs JSON.

Exit codes:
  0 — metadata updated
  1 — gh CLI error
  2 — config error
"""
import argparse
import json
import subprocess
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Edit GitHub repository metadata via gh CLI",
    )
    parser.add_argument("--repo", required=True, help="Owner/name")
    parser.add_argument("--description", help="Repository description")
    parser.add_argument("--add-topic", action="append", default=[], dest="add_topics",
                        help="Topic to add (repeatable)")
    parser.add_argument("--remove-topic", action="append", default=[], dest="remove_topics",
                        help="Topic to remove (repeatable)")
    return parser.parse_args()


def main():
    args = parse_args()
    cmd = ["gh", "repo", "edit", args.repo]
    if args.description:
        cmd.extend(["--description", args.description])
    for topic in args.add_topics:
        cmd.extend(["--add-topic", topic])
    for topic in args.remove_topics:
        cmd.extend(["--remove-topic", topic])

    if len(cmd) == 3:
        print("WARN: no metadata changes specified. Nothing to do.", file=sys.stderr)
        print(json.dumps({"repo": args.repo, "changed": False}))
        sys.exit(0)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        print("FATAL: gh CLI not found.", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("FATAL: gh repo edit timed out.", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(f"FATAL: gh repo edit failed:\n{result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    output = {"repo": args.repo, "description": args.description,
              "add_topics": args.add_topics, "remove_topics": args.remove_topics, "changed": True}
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
