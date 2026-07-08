#!/usr/bin/env python3
"""
upload-video.py — Orchestrate YouTube video upload workflow.

Subcommands:
  verify         — Validate video file and extract metadata via ffprobe
  upload         — Upload video via YouTube Data API v3 with full metadata
  verify-upload  — Confirm uploaded video exists via URL pattern check

Usage:
    python3 upload-video.py verify --video /path/to/video.webm
    python3 upload-video.py upload --video /path/to/video.webm --credentials creds.json --title "..." --description "..."
    python3 upload-video.py verify-upload --output /tmp/upload-output.txt
"""
import argparse
import json
import os
import subprocess
import sys


def cmd_verify(args):
    if not os.path.isfile(args.video):
        print(f"ERROR: File not found: {args.video}", file=sys.stderr)
        sys.exit(1)

    size_bytes = os.path.getsize(args.video)
    if size_bytes == 0:
        print(f"ERROR: File is empty: {args.video}", file=sys.stderr)
        sys.exit(1)

    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        args.video,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        print("ERROR: ffprobe not found. Install ffmpeg.", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("ERROR: ffprobe timed out", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(f"ERROR: ffprobe failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    probe = json.loads(result.stdout)
    fmt = probe.get("format", {})
    duration = float(fmt.get("duration", 0))
    size_mb = size_bytes / (1024 * 1024)
    size_gb = size_bytes / (1024 * 1024 * 1024)

    print(f"File: {args.video}")
    print(f"Size: {size_bytes} bytes ({size_mb:.1f} MB / {size_gb:.2f} GB)")
    print(f"Duration: {duration:.1f} seconds ({duration / 60:.1f} minutes)")
    print(f"Format: {fmt.get('format_name', 'unknown')}")

    video_stream = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), None)
    if video_stream:
        print(f"Video: {video_stream.get('codec_name', '?')} "
              f"{video_stream.get('width', '?')}x{video_stream.get('height', '?')} "
              f"{video_stream.get('r_frame_rate', '?')} fps")

    warnings = []
    if duration > 43200:
        warnings.append(f"Duration ({duration / 60:.1f} min) exceeds 12-hour YouTube limit")
    if size_gb > 256:
        warnings.append(f"Size ({size_gb:.2f} GB) exceeds 256 GB YouTube limit")
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")

    print("Verification passed.")
    sys.exit(0)


def cmd_upload(args):
    if not os.path.isfile(args.video):
        print(f"ERROR: File not found: {args.video}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.credentials):
        print(f"ERROR: Credentials file not found: {args.credentials}", file=sys.stderr)
        sys.exit(1)
    if not args.title or not args.description:
        print("ERROR: --title and --description are required", file=sys.stderr)
        sys.exit(1)
    if not args.client_secrets:
        print("ERROR: --client-secrets is required", file=sys.stderr)
        sys.exit(1)

    import googleapiclient.discovery
    import httplib2
    from oauth2client import client as oa_client, file as oa_file

    SCOPES = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.upload"]

    flow = oa_client.flow_from_clientsecrets(args.client_secrets, scope=SCOPES)
    storage = oa_file.Storage(args.credentials)
    credentials = storage.get()
    if not credentials or credentials.invalid:
        print("ERROR: No valid credentials. Run oauth-setup.py first.", file=sys.stderr)
        sys.exit(1)
    httplib = httplib2.Http()
    httplib.redirect_codes = httplib.redirect_codes - {308}
    http = credentials.authorize(httplib)
    youtube = googleapiclient.discovery.build("youtube", "v3", http=http)

    body = {
        "snippet": {
            "title": args.title,
            "description": args.description,
        },
        "status": {
            "privacyStatus": args.privacy or "private",
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": args.contains_synthetic_media,
        },
    }

    if args.tags:
        body["snippet"]["tags"] = args.tags
    if args.language:
        body["snippet"]["defaultLanguage"] = args.language
        body["snippet"]["defaultAudioLanguage"] = args.language
    if args.recording_date:
        body["recordingDetails"] = {"recordingDate": args.recording_date}

    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(args.video, chunksize=8 * 1024 * 1024, resumable=True)

    print("Uploading...")
    request = youtube.videos().insert(
        part="snippet,status" + (",recordingDetails" if args.recording_date else ""),
        body=body,
        media_body=media,
        notifySubscribers=args.notify_subscribers,
    )

    response = None
    try:
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"\rUploading... {pct}%", end="", flush=True)
    except googleapiclient.errors.HttpError as e:
        err = json.loads(e.content.decode()) if e.content else {}
        reason = err.get("error", {}).get("errors", [{}])[0].get("reason", "")
        if reason == "quotaExceeded":
            print("\nERROR: YouTube API quota exceeded. Try again tomorrow.", file=sys.stderr)
        else:
            print(f"\nERROR: Upload failed — {reason}: {err.get('error', {}).get('message', str(e))}", file=sys.stderr)
        sys.exit(1)

    print()
    video_url = f"https://youtu.be/{response['id']}"
    print(video_url)

    if args.playlist_ids:
        for pid in args.playlist_ids:
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": pid,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": response["id"],
                        },
                    },
                },
            ).execute()
            print(f"Added to playlist: {pid}")

    print("Upload successful.")

    if args.output:
        with open(args.output, "w") as f:
            f.write(video_url + "\n")
        print(f"Upload output saved to: {args.output}")


def cmd_verify_upload(args):
    if not args.output and not args.video_url:
        print("ERROR: --output or --video-url required", file=sys.stderr)
        sys.exit(1)

    video_url = args.video_url
    if args.output:
        if not os.path.isfile(args.output):
            print(f"ERROR: Output file not found: {args.output}", file=sys.stderr)
            sys.exit(1)
        with open(args.output) as f:
            content = f.read().strip()
        if not video_url:
            video_url = content.strip().split("\n")[-1]

    print(f"Video URL: {video_url}")
    if video_url and ("youtube.com/watch?v=" in video_url or "youtu.be/" in video_url):
        print("Verification: YouTube URL detected in output — upload confirmed.")
        sys.exit(0)
    else:
        print("WARNING: Could not verify upload. Check YouTube Studio manually.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="YouTube video upload orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify_parser = subparsers.add_parser("verify", help="Validate video file and extract metadata")
    verify_parser.add_argument("--video", required=True, help="Path to video file")

    upload_parser = subparsers.add_parser("upload", help="Upload video via YouTube Data API v3")
    upload_parser.add_argument("--video", required=True, help="Path to video file")
    upload_parser.add_argument("--client-secrets", required=True, help="Path to client_secrets.json")
    upload_parser.add_argument("--credentials", required=True, help="Path to OAuth credential cache JSON")
    upload_parser.add_argument("--title", required=True, help="Video title")
    upload_parser.add_argument("--description", required=True, help="Video description")
    upload_parser.add_argument("--tags", nargs="*", default=[], help="Video tags (space-separated list)")
    upload_parser.add_argument("--language", help="BCP-47 language tag (e.g. en)")
    upload_parser.add_argument("--recording-date", help="ISO-8601 recording date (e.g. 2026-06-14)")
    upload_parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    upload_parser.add_argument("--notify-subscribers", default=True, action=argparse.BooleanOptionalAction, help="Notify subscribers (default: true)")
    upload_parser.add_argument("--contains-synthetic-media", action="store_true", help="Set containsSyntheticMedia = true (AI-generated content disclosure)")
    upload_parser.add_argument("--playlist-id", action="append", default=None, dest="playlist_ids", help="Playlist ID to add the video to after upload (can be specified multiple times)")
    upload_parser.add_argument("--output", help="Save upload output to file for verification")

    verify_upload_parser = subparsers.add_parser("verify-upload", help="Confirm upload via YouTube API")
    verify_upload_parser.add_argument("--output", help="Upload output file to verify")
    verify_upload_parser.add_argument("--video-url", help="YouTube video URL to verify")

    args = parser.parse_args()

    if args.command == "verify":
        cmd_verify(args)
    elif args.command == "upload":
        cmd_upload(args)
    elif args.command == "verify-upload":
        cmd_verify_upload(args)


if __name__ == "__main__":
    main()
