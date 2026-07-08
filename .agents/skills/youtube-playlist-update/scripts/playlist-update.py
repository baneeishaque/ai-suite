#!/usr/bin/env python3
"""
youtube-playlist-update.py — Update YouTube playlist metadata (title, description, privacy).

Accepts a playlist ID and new metadata fields via CLI flags.
Calls YouTube Data API v3 playlists.update (PUT) with the modified snippet.

Usage:
    python3 playlist-update.py <PLAYLIST_ID> --credentials <creds.json>
        [--title "New Title"] [--description "New description"] [--privacy private]

All flags are optional — only provided fields are updated.
Existing values are preserved for omitted flags.
"""
import argparse, json, os, requests, sys


def build_parser():
    p = argparse.ArgumentParser(description="Update YouTube playlist metadata")
    p.add_argument("playlist_id", help="YouTube playlist ID to update")
    p.add_argument("--credentials", required=True, help="Path to OAuth credential cache (JSON)")
    p.add_argument("--title", help="New playlist title")
    p.add_argument("--description", help="New playlist description")
    p.add_argument("--privacy", choices=["private", "unlisted", "public"], help="New privacy status")
    return p


def main():
    args = build_parser().parse_args()

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

    # Fetch current playlist state
    r = requests.get(f"{base}/playlists?part=snippet,status&id={args.playlist_id}", headers=headers)
    if r.status_code != 200:
        print(f"ERROR: Failed to fetch playlist: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)

    items = r.json().get("items", [])
    if not items:
        print(f"ERROR: Playlist not found: {args.playlist_id}", file=sys.stderr)
        sys.exit(1)

    pl = items[0]

    # Apply updates (only non-None fields)
    if args.title is not None:
        pl["snippet"]["title"] = args.title
    if args.description is not None:
        pl["snippet"]["description"] = args.description
    if args.privacy is not None:
        pl["status"]["privacyStatus"] = args.privacy

    # PUT updated playlist
    r = requests.put(f"{base}/playlists?part=snippet,status", headers=headers, json=pl)
    if r.status_code != 200:
        print(f"ERROR: Failed to update playlist: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)

    updated = r.json()
    print(f"Updated: {updated['id']}")
    print(f"  Title:       {updated['snippet']['title']}")
    print(f"  Description: {updated['snippet'].get('description', '')}")
    print(f"  Privacy:     {updated['status']['privacyStatus']}")


if __name__ == "__main__":
    main()
