#!/usr/bin/env python3
"""
gh-repo-create.py — Tier 1 (Python) per scripting-language-selection-rules.md §2.3

Wrap `gh repo create` with structured arguments. Supports source directory,
visibility, remote name, and push flag. Outputs JSON for composer consumption.

Exit codes:
  0 — repo created (or already existed)
  1 — gh CLI error (missing, auth failure, API error)
  2 — config error (missing required args)
"""
import argparse
import json
import subprocess
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a GitHub repository via gh CLI",
    )
    parser.add_argument("--repo", required=True, help="Owner/name (e.g. octocat/hello-world)")
    parser.add_argument("--source", default=".", help="Path to local directory to push (default: .)")
    parser.add_argument("--visibility", choices=["public", "private", "internal"], default="private")
    parser.add_argument("--remote", default="origin", help="Remote name (default: origin)")
    parser.add_argument("--push", action="store_true", default=True, help="Push local commits after creation")
    parser.add_argument("--no-push", action="store_false", dest="push")
    return parser.parse_args()


def main():
    args = parse_args()
    cmd = [
        "gh", "repo", "create", args.repo,
        "--source", args.source,
        "--visibility", args.visibility,
        "--remote", args.remote,
    ]
    if args.push:
        cmd.append("--push")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        print("FATAL: gh CLI not found. Install via `brew install gh` or equivalent.", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("FATAL: gh repo create timed out after 120s.", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(f"FATAL: gh repo create failed:\n{result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    url = result.stdout.strip()
    output = {"repo": args.repo, "url": url, "created": True}
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
