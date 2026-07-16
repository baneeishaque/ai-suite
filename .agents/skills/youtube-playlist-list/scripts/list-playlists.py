#!/usr/bin/env python3
"""
list-playlists.py — List authenticated user's YouTube playlists.

Reads OAuth credentials, queries the YouTube Data API v3 playlists endpoint,
and prints a tabular listing: ID | TITLE | VIDEO_COUNT.

Usage:
    python3 list-playlists.py --credentials /path/to/credentials.json
"""
import argparse
import json
import sys

import requests


def parse_args():
    parser = argparse.ArgumentParser(description="List YouTube playlists")
    parser.add_argument("--credentials", required=True, help="Path to OAuth credential cache")
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.credentials) as f:
        creds = json.load(f)

    access_token = creds.get("access_token")
    if not access_token:
        print("ERROR: No access_token found in credentials", file=sys.stderr)
        sys.exit(1)

    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://www.googleapis.com/youtube/v3/playlists"
    params = {
        "part": "snippet,contentDetails",
        "mine": "true",
        "maxResults": 50,
    }

    playlists = []
    while url:
        resp = requests.get(url, headers=headers, params=params if "?" not in url else {})
        if resp.status_code == 401:
            print("ERROR: 401 Unauthorized — token may be expired. Run oauth-token-refresh.py", file=sys.stderr)
            sys.exit(1)
        if resp.status_code != 200:
            print(f"ERROR: API returned {resp.status_code}: {resp.text}", file=sys.stderr)
            sys.exit(1)

        data = resp.json()
        playlists.extend(data.get("items", []))
        url = data.get("nextPageToken", "")
        if url:
            url = f"https://www.googleapis.com/youtube/v3/playlists?part=snippet,contentDetails&mine=true&maxResults=50&pageToken={url}"
            params = {}

    if not playlists:
        print("No playlists found.")
        sys.exit(0)

    print(f"{'PLAYLIST_ID':<42} | TITLE")
    print("-" * 42 + "-+-" + "-" * 40)
    for pl in playlists:
        pid = pl["id"]
        title = pl["snippet"]["title"]
        count = pl["contentDetails"]["itemCount"]
        print(f"{pid:<42} | {title} ({count} videos)")


if __name__ == "__main__":
    main()
