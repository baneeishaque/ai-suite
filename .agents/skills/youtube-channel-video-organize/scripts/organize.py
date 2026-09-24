#!/usr/bin/env python3
"""
organize.py — Orchestrate YouTube channel video organization into playlists.

Subcommands:
  list-videos     — List all channel videos (JSON lines).
  list-playlists  — List all channel playlists (JSON lines).
  assign          — Read a JSON mapping file and add videos to playlists.

Usage:
    python3 organize.py list-videos --credentials <path>
    python3 organize.py list-playlists --credentials <path>
    python3 organize.py assign --credentials <path> --mapping <mapping.json>

Tier: 1 (Python 3.12+ with requests) — lightweight orchestrator composing base skills.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def cmd_list_videos(args):
    script = Path(__file__).resolve().parent / "../../youtube-channel-video-list/scripts/channel-video-list.py"
    if not script.exists():
        print(f"ERROR: Base script not found: {script}", file=sys.stderr)
        sys.exit(1)
    result = subprocess.run(
        [sys.executable, str(script), "--credentials", args.credentials, "--format", "json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    print(result.stdout, end="")


def cmd_list_playlists(args):
    script = Path(__file__).resolve().parent / "../../youtube-playlist-list/scripts/list-playlists.py"
    if not script.exists():
        print(f"ERROR: Base script not found: {script}", file=sys.stderr)
        sys.exit(1)
    result = subprocess.run(
        [sys.executable, str(script), "--credentials", args.credentials],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    print(result.stdout, end="")


def cmd_assign(args):
    add_script = Path(__file__).resolve().parent / "../../youtube-playlist-item-add/scripts/playlist-item-add.py"
    if not add_script.exists():
        print(f"ERROR: Base script not found: {add_script}", file=sys.stderr)
        sys.exit(1)

    with open(args.mapping) as f:
        mapping = json.load(f)

    assignments = mapping.get("assignments", [])
    if not assignments:
        print("No assignments found in mapping file.")
        sys.exit(0)

    success = 0
    failed = 0
    for entry in assignments:
        video_id = entry["video_id"]
        playlist_id = entry["playlist_id"]
        print(f"Adding {video_id} → {playlist_id} ... ", end="")
        result = subprocess.run(
            [sys.executable, str(add_script), video_id, playlist_id, "--credentials", args.credentials],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print("OK")
            success += 1
        else:
            print(f"FAILED: {result.stderr.strip()}")
            failed += 1

    print(f"\nDone: {success} succeeded, {failed} failed.")
    if failed:
        sys.exit(1)


def parse_args():
    p = argparse.ArgumentParser(description="Organize YouTube channel videos into playlists")
    sub = p.add_subparsers(dest="command", required=True)

    p_list_videos = sub.add_parser("list-videos", help="List all channel videos")
    p_list_videos.add_argument("--credentials", required=True)

    p_list_playlists = sub.add_parser("list-playlists", help="List all playlists")
    p_list_playlists.add_argument("--credentials", required=True)

    p_assign = sub.add_parser("assign", help="Assign videos to playlists from mapping file")
    p_assign.add_argument("--credentials", required=True)
    p_assign.add_argument("--mapping", required=True, help="JSON mapping file with assignments array")

    return p.parse_args()


def main():
    args = parse_args()
    dispatch = {
        "list-videos": cmd_list_videos,
        "list-playlists": cmd_list_playlists,
        "assign": cmd_assign,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
