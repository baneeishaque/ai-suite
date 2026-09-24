#!/usr/bin/env python3
"""
video-metadata-update.py — Update advanced YouTube video metadata via Data API v3.

Sets fields not configurable during initial upload:
  - categoryId (28 = Science & Technology)
  - selfDeclaredMadeForKids
  - embeddable
  - license (youtube | creativeCommon)
  - defaultLanguage / defaultAudioLanguage
  - publicStatsViewable (show like count)
  - contentRating.ytRating (age restriction)

Usage:
    python3 video-metadata-update.py <VIDEO_ID> --client-secrets <path> --credentials <path>
"""
import argparse
import sys

import googleapiclient.discovery
import httplib2
from oauth2client import client, file

SCOPES = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.upload"]


def parse_args():
    p = argparse.ArgumentParser(description="Update YouTube video metadata")
    p.add_argument("video_id", help="YouTube video ID")
    p.add_argument("--client-secrets", required=True, help="Path to client_secrets.json")
    p.add_argument("--credentials", required=True, help="Path to credential cache")
    p.add_argument("--category-id", default="28", help="YouTube category ID (default: 28 = Science & Technology)")
    p.add_argument("--language", default="en", help="BCP-47 language tag for metadata (default: en)")
    p.add_argument("--audio-language", default=None, help="BCP-47 language tag for audio (default: same as --language)")
    p.add_argument("--made-for-kids", action="store_true", help="Set madeForKids = true (default: false)")
    p.add_argument("--embeddable", action="store_true", help="Set embeddable = true (default: false)")
    p.add_argument("--public-stats", action="store_true", help="Set publicStatsViewable = true (default: false)")
    p.add_argument("--license", default="youtube", choices=["youtube", "creativeCommon"], help="Video license")
    p.add_argument("--contains-synthetic-media", action="store_true", help="Set containsSyntheticMedia = true (AI-generated content disclosure)")
    p.add_argument("--age-restricted", action="store_true", help="Set contentRating ytRating = ytAgeRestricted")
    return p.parse_args()


def get_service(client_secrets_file, credentials_file):
    flow = client.flow_from_clientsecrets(client_secrets_file, scope=SCOPES)
    storage = file.Storage(credentials_file)
    credentials = storage.get()
    if not credentials or credentials.invalid:
        print("ERROR: No valid credentials. Run oauth-setup.py first.", file=sys.stderr)
        sys.exit(1)
    httplib = httplib2.Http()
    httplib.redirect_codes = httplib.redirect_codes - {308}
    http = credentials.authorize(httplib)
    return googleapiclient.discovery.build("youtube", "v3", http=http)


def main():
    args = parse_args()
    youtube = get_service(args.client_secrets, args.credentials)

    resp = youtube.videos().list(part="snippet,status,contentDetails", id=args.video_id).execute()
    if not resp.get("items"):
        print(f"ERROR: Video {args.video_id} not found", file=sys.stderr)
        sys.exit(1)

    video = resp["items"][0]

    video["snippet"]["categoryId"] = args.category_id
    audio_lang = args.audio_language if args.audio_language else args.language
    video["snippet"]["defaultLanguage"] = args.language
    video["snippet"]["defaultAudioLanguage"] = audio_lang

    video["status"]["selfDeclaredMadeForKids"] = args.made_for_kids
    video["status"]["embeddable"] = args.embeddable
    video["status"]["license"] = args.license
    video["status"]["publicStatsViewable"] = args.public_stats
    video["status"]["containsSyntheticMedia"] = args.contains_synthetic_media

    if args.age_restricted:
        if "contentRating" not in video["contentDetails"]:
            video["contentDetails"]["contentRating"] = {}
        video["contentDetails"]["contentRating"]["ytRating"] = "ytAgeRestricted"

    update_body = {
        "id": args.video_id,
        "snippet": video["snippet"],
        "status": video["status"],
        "contentDetails": video["contentDetails"],
    }

    result = youtube.videos().update(part="snippet,status,contentDetails", body=update_body).execute()

    s = result["status"]
    cd = result["contentDetails"]
    print(f"Updated: https://youtu.be/{result['id']}")
    print(f"  Category: {result['snippet']['categoryId']}")
    print(f"  Metadata language: {result['snippet']['defaultLanguage']}")
    print(f"  Audio language: {result['snippet'].get('defaultAudioLanguage', 'N/A')}")
    print(f"  Made for kids: {s['selfDeclaredMadeForKids']}")
    print(f"  Embeddable: {s['embeddable']}")
    print(f"  License: {s['license']}")
    print(f"  Public stats: {s.get('publicStatsViewable', 'N/A')}")
    print(f"  AI disclosure (containsSyntheticMedia): {s.get('containsSyntheticMedia', 'N/A')}")
    if args.age_restricted:
        print(f"  Age restricted: {cd.get('contentRating', {}).get('ytRating', 'NOT SET')}")
        if cd.get("contentRating", {}).get("ytRating") != "ytAgeRestricted":
            print("  WARNING: ytAgeRestricted may not persist for this account type. Set via YouTube Studio.")

    print("\nStudio-only fields (not settable via API):")
    print("  - Age restriction (advanced) — YouTube Studio → Advanced")
    print("  - Comments off — YouTube Studio → Comments")
    print("  - Don't publish to sub feed — YouTube Studio → Advanced")
    print("  - Don't allow remix — YouTube Studio → Video details")


if __name__ == "__main__":
    main()
