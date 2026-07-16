#!/usr/bin/env python3
"""
playlist-create.py — Create a YouTube playlist via Data API v3.

Reads OAuth credentials, calls playlists.insert, and prints the new playlist ID.

Usage:
    python3 playlist-create.py --credentials /path/to/credentials.json
        --title "My Playlist" [--description "..." [--privacy private]

Tier: 1 (Python 3.12+ with requests) — standard Data API wrapper.
"""
import argparse
import json
import sys

import requests


def parse_args():
    p = argparse.ArgumentParser(description="Create a YouTube playlist")
    p.add_argument("--credentials", required=True, help="Path to OAuth credential cache")
    p.add_argument("--title", required=True, help="Playlist title")
    p.add_argument("--description", default="", help="Playlist description")
    p.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"],
                   help="Playlist privacy status (default: private)")
    return p.parse_args()


def main():
    args = parse_args()

    with open(args.credentials) as f:
        creds = json.load(f)

    access_token = creds.get("access_token")
    if not access_token:
        print("ERROR: No access_token found in credentials", file=sys.stderr)
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    body = {
        "snippet": {
            "title": args.title,
            "description": args.description,
        },
        "status": {
            "privacyStatus": args.privacy,
        },
    }
    resp = requests.post(
        "https://www.googleapis.com/youtube/v3/playlists?part=snippet,status",
        headers=headers, json=body,
    )
    if resp.status_code == 401:
        print("ERROR: 401 Unauthorized — token may be expired. Run oauth-token-refresh.py", file=sys.stderr)
        sys.exit(1)
    if resp.status_code != 200:
        print(f"ERROR: API returned {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    pid = data["id"]
    print(pid)


if __name__ == "__main__":
    main()
