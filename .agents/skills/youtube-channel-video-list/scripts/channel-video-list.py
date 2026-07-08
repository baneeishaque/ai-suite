#!/usr/bin/env python3
"""
channel-video-list.py — List all uploaded videos on the authenticated YouTube channel.

Reads OAuth credentials, queries the uploads playlist via playlistItems.list,
and outputs JSON lines: video_id, title, published_at.

Usage:
    python3 channel-video-list.py --credentials /path/to/credentials.json

Tier: 1 (Python 3.12+ with requests) — standard Data API wrapper with pagination.
"""
import argparse
import json
import sys

import requests


def parse_args():
    p = argparse.ArgumentParser(description="List all uploaded videos on the authenticated YouTube channel")
    p.add_argument("--credentials", required=True, help="Path to OAuth credential cache")
    p.add_argument("--format", choices=["json", "table"], default="table",
                   help="Output format (default: table)")
    return p.parse_args()


def get_uploads_playlist_id(access_token):
    """Get the authenticated user's uploads playlist ID."""
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(
        "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true",
        headers=headers,
    )
    if resp.status_code != 200:
        print(f"ERROR: Failed to get channel info: {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)
    data = resp.json()
    items = data.get("items", [])
    if not items:
        print("ERROR: No channel found for authenticated user", file=sys.stderr)
        sys.exit(1)
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def main():
    args = parse_args()

    with open(args.credentials) as f:
        creds = json.load(f)

    access_token = creds.get("access_token")
    if not access_token:
        print("ERROR: No access_token found in credentials", file=sys.stderr)
        sys.exit(1)

    uploads_playlist_id = get_uploads_playlist_id(access_token)

    headers = {"Authorization": f"Bearer {access_token}"}
    videos = []
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "snippet,contentDetails",
        "playlistId": uploads_playlist_id,
        "maxResults": 50,
    }

    while url:
        resp = requests.get(url, headers=headers, params=params if "?" not in url else {})
        if resp.status_code == 401:
            print("ERROR: 401 Unauthorized — token may be expired. Run oauth-token-refresh.py", file=sys.stderr)
            sys.exit(1)
        if resp.status_code != 200:
            print(f"ERROR: API returned {resp.status_code}: {resp.text}", file=sys.stderr)
            sys.exit(1)

        data = resp.json()
        for item in data.get("items", []):
            video_id = item["contentDetails"]["videoId"]
            title = item["snippet"]["title"]
            published_at = item["snippet"]["publishedAt"]
            videos.append({
                "video_id": video_id,
                "title": title,
                "published_at": published_at,
            })

        url = data.get("nextPageToken", "")
        if url:
            url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&playlistId={uploads_playlist_id}&maxResults=50&pageToken={url}"
            params = {}

    if not videos:
        print("No videos found on the channel.")
        sys.exit(0)

    if args.format == "json":
        for v in videos:
            print(json.dumps(v))
    else:
        print(f"{'VIDEO_ID':<14} | {'PUBLISHED':<20} | TITLE")
        print("-" * 14 + "-+-" + "-" * 20 + "-+-" + "-" * 60)
        for v in videos:
            pub = v["published_at"][:10]
            print(f"{v['video_id']:<14} | {pub:<20} | {v['title']}")


if __name__ == "__main__":
    main()
