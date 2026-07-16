#!/usr/bin/env python3
"""
gh-pr-edit.py — View and edit GitHub PR details via gh CLI.

Subcommands:
  view   — View current PR title, body, head ref, state
  edit   — Update PR title and/or body (handles multi-line body via temp file)

Environment:
  GH_TOKEN  — GitHub PAT (optional; overridden by --token)
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile


def run_gh(args, token=None):
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
    cmd = ["gh"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"Error: gh {' '.join(args)}", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(1)
    return result.stdout


def cmd_view(args):
    output = run_gh([
        "pr", "view", str(args.pr),
        "--repo", args.repo,
        "--json", "title,body,headRefName,number,url,state,author"
    ], token=args.token)
    data = json.loads(output)
    print(json.dumps(data, indent=2))


def cmd_edit(args):
    gh_args = ["pr", "edit", str(args.pr), "--repo", args.repo]
    cleanup = []

    if args.title:
        gh_args.extend(["--title", args.title])

    if args.body:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
        f.write(args.body)
        f.close()
        cleanup.append(f.name)
        gh_args.extend(["--body-file", f.name])
    elif args.body_file:
        gh_args.extend(["--body-file", args.body_file])

    if len(gh_args) <= 4:
        print("Nothing to update. Provide --title and/or --body/--body-file.")
        sys.exit(1)

    run_gh(gh_args, token=args.token)

    for path in cleanup:
        os.unlink(path)

    print(f"PR #{args.pr} updated successfully.")


def main():
    parser = argparse.ArgumentParser(
        description="View and edit GitHub PR details via gh CLI"
    )
    parser.add_argument("--token", help="GitHub PAT (overrides GH_TOKEN env)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    view_p = subparsers.add_parser("view", help="View PR title, body, head ref, state")
    view_p.add_argument("--pr", type=int, required=True)
    view_p.add_argument("--repo", required=True, help="owner/repo")
    view_p.set_defaults(func=cmd_view)

    edit_p = subparsers.add_parser("edit", help="Update PR title and/or body")
    edit_p.add_argument("--pr", type=int, required=True)
    edit_p.add_argument("--repo", required=True, help="owner/repo")
    edit_p.add_argument("--title", help="New PR title")
    edit_p.add_argument("--body", help="New PR body text (multi-line OK)")
    edit_p.add_argument("--body-file", help="Path to file containing PR body")
    edit_p.set_defaults(func=cmd_edit)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
