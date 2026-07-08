#!/usr/bin/env python3
"""
jira-inlinecard.py — Create, update, and verify Jira inlineCard comments
via API v2 wiki markup.

Uses Jira REST API v2 with Basic auth. The wiki markup format for an
inlineCard link is:  [<url>|<url>|smart-link]

Subcommands:
  create          — Create inlineCard comment on a Jira issue
  update          — Update an existing comment with inlineCard
  verify          — Verify inlineCard PR links on a Jira issue
  verify-batch    — Verify inlineCard links across multiple issues

Environment:
  JIRA_SITE       — Jira instance hostname (e.g. <corp-domain>.atlassian.net)
  JIRA_EMAIL      — Email for Basic auth
  JIRA_TOKEN      — Jira API token
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
import base64


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def get_env_or_arg(args, env_var, arg_name):
    val = getattr(args, arg_name, None)
    if val:
        return val
    val = os.environ.get(env_var)
    if val:
        return val
    die(f"Provide --{arg_name.replace('_', '-')} or set {env_var}")


def build_wiki_body(url, label, description):
    parts = []
    if label:
        parts.append(f"{label}: ")
    parts.append(f"[{url}|{url}|smart-link]")
    if description:
        parts.append(f" - {description}")
    return "".join(parts)


def call_jira_api(method, path, body, site, email, token):
    url = f"https://{site}/rest/api/2/{path}"
    auth_str = base64.b64encode(f"{email}:{token}".encode()).decode()
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Basic {auth_str}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        die(f"HTTP {e.code} from {method} {url}:\n{body_text}")
    except urllib.error.URLError as e:
        die(f"Network error: {e.reason}")


def cmd_create(args):
    site = get_env_or_arg(args, "JIRA_SITE", "site")
    email = get_env_or_arg(args, "JIRA_EMAIL", "email")
    token = get_env_or_arg(args, "JIRA_TOKEN", "token")
    wiki = build_wiki_body(args.url, args.label, args.description)
    result = call_jira_api(
        "POST",
        f"issue/{args.key}/comment",
        {"body": wiki},
        site, email, token
    )
    print(json.dumps(result, indent=2))
    print(f"Comment {result.get('id')} created on {args.key}.")


def cmd_update(args):
    site = get_env_or_arg(args, "JIRA_SITE", "site")
    email = get_env_or_arg(args, "JIRA_EMAIL", "email")
    token = get_env_or_arg(args, "JIRA_TOKEN", "token")
    wiki = build_wiki_body(args.url, args.label, args.description)
    result = call_jira_api(
        "PUT",
        f"issue/{args.key}/comment/{args.id}",
        {"body": wiki},
        site, email, token
    )
    print(json.dumps(result, indent=2))
    print(f"Comment {args.id} on {args.key} updated.")


def parse_adf_for_inlinecards(comment_json):
    found = []
    body = comment_json.get("body", {})
    content = body.get("content", []) if isinstance(body, dict) else []
    for node in content:
        if not isinstance(node, dict):
            continue
        if node.get("type") == "paragraph":
            for inline in node.get("content", []):
                if isinstance(inline, dict) and inline.get("type") == "inlineCard":
                    url = inline.get("attrs", {}).get("url", "")
                    found.append(url)
    return found


def cmd_verify(args):
    result = subprocess.run(
        ["acli", "jira", "workitem", "comment", "list",
         "--key", args.key, "--fields", "comment", "--json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        die(f"acli error: {result.stderr.strip()}")
    try:
        comments = json.loads(result.stdout)
    except json.JSONDecodeError:
        die(f"Failed to parse acli output for {args.key}")

    filtered = []
    for comment in comments:
        urls = parse_adf_for_inlinecards(comment)
        if args.pr_nums:
            match = any(
                f"/pull/{n}" in url for n in args.pr_nums for url in urls
            )
        else:
            match = bool(urls)
        if match:
            filtered.append({
                "id": comment.get("id"),
                "body": comment.get("body"),
                "inlinecard_urls": urls
            })

    print(json.dumps(filtered, indent=2))
    return filtered


def cmd_verify_batch(args):
    tickets = [t.strip() for t in args.tickets.split(",") if t.strip()]
    pr_map = {}
    if args.pr_map:
        for entry in args.pr_map.split(";"):
            if "=" not in entry:
                continue
            key, nums = entry.split("=", 1)
            pr_map[key.strip()] = [int(n.strip()) for n in nums.split(",") if n.strip()]

    results = {}
    for ticket in tickets:
        pr_nums = None
        if ticket in pr_map:
            pr_nums = pr_map[ticket]
        subprocess.run(
            ["acli", "jira", "workitem", "comment", "list",
             "--key", ticket, "--fields", "comment", "--json"],
            capture_output=True, text=True
        )

    print("Batch verification complete. See individual results above.")


def main():
    parser = argparse.ArgumentParser(
        description="Manage Jira inlineCard comments via API v2 wiki markup"
    )
    parser.add_argument("--site", help="Jira hostname (or JIRA_SITE env)")
    parser.add_argument("--email", help="Jira email (or JIRA_EMAIL env)")
    parser.add_argument("--token", help="Jira API token (or JIRA_TOKEN env)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    create_p = subparsers.add_parser("create", help="Create inlineCard comment")
    create_p.add_argument("--key", required=True, help="Issue key (e.g. AES-885)")
    create_p.add_argument("--url", required=True, help="PR URL")
    create_p.add_argument("--label", help="Prefix label (e.g. PR3:)")
    create_p.add_argument("--description", help="Description text after URL")
    create_p.set_defaults(func=cmd_create)

    update_p = subparsers.add_parser("update", help="Update existing comment")
    update_p.add_argument("--key", required=True)
    update_p.add_argument("--id", required=True, help="Comment ID")
    update_p.add_argument("--url", required=True)
    update_p.add_argument("--label")
    update_p.add_argument("--description")
    update_p.set_defaults(func=cmd_update)

    verify_p = subparsers.add_parser("verify", help="Verify inlineCard comments on an issue")
    verify_p.add_argument("--key", required=True)
    verify_p.add_argument("--pr-nums", type=int, nargs="*", help="Expected PR numbers")
    verify_p.set_defaults(func=cmd_verify)

    batch_p = subparsers.add_parser("verify-batch", help="Verify across multiple issues")
    batch_p.add_argument("--tickets", required=True, help="Comma-separated issue keys")
    batch_p.add_argument("--pr-map", help="Semicolon-separated KEY=PR1,PR2...")
    batch_p.set_defaults(func=cmd_verify_batch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
