#!/usr/bin/env python3
"""
playlist-item-add.py — Add an existing video to a YouTube playlist via Data API v3.

Reads OAuth credentials, calls playlistItems.insert, and prints the playlist item ID.

Usage:
    python3 playlist-item-add.py <VIDEO_ID> <PLAYLIST_ID> --credentials /path/to/credentials.json

Tier: 1 (Python 3.12+ with requests) — standard Data API wrapper.
"""
import argparse
import json
import sys

import requests


def parse_args():
    p = argparse.ArgumentParser(description="Add a video to a YouTube playlist")
    p.add_argument("video_id", help="YouTube video ID to add")
    p.add_argument("playlist_id", help="Target playlist ID")
    p.add_argument("--credentials", required=True, help="Path to OAuth credential cache")
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
            "playlistId": args.playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": args.video_id,
            },
        },
    }
    resp = requests.post(
        "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet",
        headers=headers, json=body,
    )
    if resp.status_code == 401:
        print("ERROR: 401 Unauthorized — token may be expired. Run oauth-token-refresh.py", file=sys.stderr)
        sys.exit(1)
    if resp.status_code != 200:
        print(f"ERROR: API returned {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    print(f"Added: https://youtu.be/{args.video_id} to playlist {args.playlist_id} (item ID: {data['id']})")


if __name__ == "__main__":
    main()
