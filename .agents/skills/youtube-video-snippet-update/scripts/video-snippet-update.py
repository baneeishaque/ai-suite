#!/usr/bin/env python3
"""
video-snippet-update.py — Update YouTube video title, description, and tags via Data API v3.

Reads OAuth credentials, fetches current snippet, applies deltas, and PUTs the result.

Usage:
    python3 video-snippet-update.py <VIDEO_ID> --credentials <creds.json>
        [--title "New Title"] [--description "New desc"] [--tags "tag1 tag2"]

All flags are optional — only provided fields are updated.
Existing values are preserved for omitted flags.
"""
import argparse
import json
import os
import sys

import requests


def parse_args():
    p = argparse.ArgumentParser(description="Update YouTube video snippet (title, description, tags)")
    p.add_argument("video_id", help="YouTube video ID to update")
    p.add_argument("--credentials", required=True, help="Path to OAuth credential cache (JSON)")
    p.add_argument("--title", help="New video title (max 100 characters)")
    p.add_argument("--description", help="New video description")
    p.add_argument("--tags", help="Space-separated tags (e.g. 'tag1 tag2')")
    return p.parse_args()


def main():
    args = parse_args()

    if not args.title and not args.description and not args.tags:
        print("ERROR: At least one of --title, --description, or --tags must be provided", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(args.credentials):
        print(f"ERROR: Credentials file not found: {args.credentials}", file=sys.stderr)
        sys.exit(1)

    with open(args.credentials) as f:
        creds = json.load(f)

    access_token = creds.get("access_token")
    if not access_token:
        print("ERROR: access_token not found in credentials", file=sys.stderr)
        sys.exit(1)

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    base = "https://www.googleapis.com/youtube/v3"

    # Fetch current video snippet
    r = requests.get(f"{base}/videos?part=snippet&id={args.video_id}", headers=headers)
    if r.status_code != 200:
        print(f"ERROR: Failed to fetch video: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)

    items = r.json().get("items", [])
    if not items:
        print(f"ERROR: Video not found: {args.video_id}", file=sys.stderr)
        sys.exit(1)

    video = items[0]

    # Apply updates (only non-None fields)
    if args.title is not None:
        video["snippet"]["title"] = args.title
    if args.description is not None:
        video["snippet"]["description"] = args.description
    if args.tags is not None:
        video["snippet"]["tags"] = args.tags.split()

    # PUT updated video snippet
    r = requests.put(f"{base}/videos?part=snippet", headers=headers, json=video)
    if r.status_code != 200:
        print(f"ERROR: Failed to update video: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)

    updated = r.json()
    s = updated["snippet"]
    print(f"Updated: https://youtu.be/{updated['id']}")
    print(f"  Title:       {s['title']}")
    print(f"  Description: {s.get('description', '')[:80]}{'...' if len(s.get('description', '')) > 80 else ''}")
    print(f"  Tags:        {', '.join(s.get('tags', []))}")


if __name__ == "__main__":
    main()
